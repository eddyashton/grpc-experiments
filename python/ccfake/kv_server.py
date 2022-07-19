from collections import defaultdict
from concurrent import futures
from enum import Enum
from threading import Thread
from loguru import logger as LOG
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
from functools import partial

import argparse
import grpc
import time
import hashlib

import registry_pb2
import registry_pb2_grpc
import kv_pb2
import kv_pb2_grpc

import crypto


DEFAULT_DISPATCH_CATEGORIES = {"foo", "bar"}


class ExecutorState(Enum):
    Registered = 0
    Ready = 1
    Executing = 2


class Executor:
    def __init__(self, category):
        self.state = ExecutorState.Registered
        self.category = category


class Registry(registry_pb2_grpc.RegistryServicer):
    def __init__(self, categories):
        self.allowed_categories = categories
        self.ready_executors = {category: [] for category in categories}
        self.all_executors = {}
        self._encoded_client_certs = b""
        self.pending_requests = []

    def _mark_ready(self, executor_id):
        assert executor_id in self.all_executors, executor_id

        ex = self.all_executors[executor_id]
        ex.state = ExecutorState.Ready
        self.ready_executors[ex.category].append(ex)

    def Register(self, request, context):
        ret = registry_pb2.RegisterResponse()
        if request.dispatch_category not in self.allowed_categories:
            ret.accepted = False
            allowed_s = "\n".join(self.allowed_categories.keys())
            ret.error = f"'{request.dispatch_category}' is not a known dispatch category.\nAllowed categories are:\n{allowed_s}"

        if request.executor_ident in self.all_executors:
            ret.accepted = False
            ret.error = f"Executor with this identity is already registered. Identity is:\n{request.executor_ident}"
        else:
            self.all_executors[request.executor_ident] = Executor(
                request.dispatch_category
            )
            ret.accepted = True
            self._encoded_client_certs += b"\n" + request.executor_ident
            LOG.trace(f"New executor registered for {request.dispatch_category}")
            LOG.trace(f"Acceptable client certs are now:\n{self._encoded_client_certs}")

        return ret


class Tx:
    def __init__(self, kv):
        self.writes = defaultdict(dict)
        self.kv = kv

    def get(self, table, key):
        if table in self.writes:
            t = self.writes[table]
            if key in t:
                return t[key]
        if table in self.kv:
            t = self.kv[table]
            if key in t:
                return t[key]
        return None

    def put(self, table, key, value):
        existed = (table in self.writes and key in self.writes[table]) or (
            table in self.kv and key in self.kv[table]
        )
        self.writes[table][key] = value
        return existed


class KV(kv_pb2_grpc.KVServicer):
    def __init__(self, registry):
        self.kv = defaultdict(dict)
        self.txs = {}
        self.registry = registry

    def _get_caller(self, context):
        return context.auth_context()["x509_pem_cert"][0]

    def _short_name(self, context):
        caller = self._get_caller(context)
        return hashlib.md5(caller).hexdigest()[:6]

    def Ready(self, request, context):
        caller = self._get_caller(context)
        short_name = self._short_name(context)
        LOG.trace(f"Ready called by {short_name}")

        while True:
            self.registry._mark_ready(caller)

            while len(self.registry.pending_requests) == 0:
                time.sleep(0.1)

            assert caller not in self.txs, "Ready called multiple times"
            tx = Tx(self.kv)
            self.txs[caller] = tx

            req = self.registry.pending_requests.pop(0)

            LOG.info(f"Dispatching a new request to {short_name}")

            ret = kv_pb2.BeginTx()
            ret.uri = req[0]
            ret.body = req[1]
            tx.http_response = req[2]

            yield ret

    def Get(self, request, context):
        caller = self._get_caller(context)
        LOG.trace(f"Get called by {caller}")

        assert caller in self.txs, "Get called out-of-order"
        tx = self.txs[caller]

        ret = kv_pb2.GetResponse()
        v = tx.get(request.table, request.key)
        if v is not None:
            ret.value = v
        return ret

    def Put(self, request, context):
        caller = self._get_caller(context)
        LOG.trace(f"Put called by {caller}")

        assert caller in self.txs, "Put called out-of-order"
        tx = self.txs[caller]

        exists = tx.put(request.table, request.key, request.value)

        ret = kv_pb2.PutResponse(existed=exists)
        return ret

    def ApplyTx(self, request, context):
        caller = self._get_caller(context)
        LOG.trace(f"ApplyTx called by {caller}")

        assert caller in self.txs, "ApplyTx called out-of-order"
        tx = self.txs[caller]
        for table, entries in tx.writes.items():
            t = self.kv[table]
            for k, v in entries.items():
                t[k] = v

        del self.txs[caller]

        tx.http_response.status_code = request.code
        tx.http_response.body = request.body
        tx.http_response.set = True

        ret = kv_pb2.ApplyResponse()
        return ret


def encode_accepted_client_certs(registry):
    # TODO: Constructing this on every session is unnecessarily expensive
    certs = b"\n".join(
        ident
        for cat, executors in registry.executors.items()
        for ident, _ in executors.items()
    )
    LOG.warning(f"Returning accepted client certs:\n{certs}")
    return certs


def fetch_server_cert_config(server_ident, registry):
    def fn():
        server_credentials = grpc.ssl_server_certificate_configuration(
            server_ident, registry._encoded_client_certs
        )
        return server_credentials

    return fn


class HttpResult:
    def __init__(self):
        self.set = False


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, registry, *args, **kwargs):
        self.registry = registry
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def _process_request(self):
        dispatch_string = f"{self.command} {self.path}"
        LOG.warning(f"Processing {dispatch_string} request")
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len)
        LOG.warning(f"Body: {body}")

        result = HttpResult()
        self.registry.pending_requests.append((dispatch_string, body, result))

        while not result.set:
            time.sleep(0.1)

        self.send_response(result.status_code)
        body = result.body
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._process_request()

    def do_POST(self):
        self._process_request()

    def log_message(self, fmt, *args):  # pylint: disable=arguments-differ
        LOG.trace(f"MyHTTPRequestHandler: {fmt % args}")


def serve(ca_out, categories):
    LOG.info("Registering workers in the following categories:")
    for cat in categories:
        LOG.info(f"  {cat}")

    # Generate a fresh key-pair. Write public cert to disk
    key_priv_pem, _ = crypto.generate_rsa_keypair(2048)
    cert_pem = crypto.generate_cert(key_priv_pem, cn="localhost", ca=True)
    server_cert_path = ca_out
    with open(server_cert_path, "wb") as f:
        f.write(cert_pem)
        LOG.info(f"Wrote server's cert to {server_cert_path}")
    server_ident = ((key_priv_pem, cert_pem),)

    # Listen for Registration protocol
    registration_server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    registry = Registry(categories=categories)
    registry_pb2_grpc.add_RegistryServicer_to_server(registry, registration_server)
    registration_server_address = "localhost:50051"
    static_credentials = grpc.ssl_server_credentials(server_ident)
    LOG.info(f"Listening for registrations on {registration_server_address}")
    registration_server.add_secure_port(registration_server_address, static_credentials)

    # Listen for KV protocol
    kv_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kv = KV(registry)
    kv_pb2_grpc.add_KVServicer_to_server(kv, kv_server)
    dynamic_creds = grpc.dynamic_ssl_server_credentials(
        grpc.ssl_server_certificate_configuration(server_ident),
        fetch_server_cert_config(server_ident, registry),
        require_client_authentication=True,
    )
    kv_server_address = "localhost:50052"
    LOG.info(f"Listening for KV traffic on {kv_server_address}")
    kv_server.add_secure_port(kv_server_address, dynamic_creds)

    # Listen on both gRPC servers
    kv_thread = Thread(target=lambda: kv_server.start())
    kv_thread.start()
    registration_thread = Thread(target=lambda: registration_server.start())
    registration_thread.start()

    # Listen for client HTTP commands
    http_address = "127.0.0.1"
    http_port = 8000
    httpd = ThreadingHTTPServer(
        (http_address, http_port), partial(MyHTTPRequestHandler, registry)
    )
    LOG.info(f"Listening for client requests on {http_address}:{http_port}")

    LOG.info("Running...")
    try:
        httpd.serve_forever()
    except:
        pass

    # Shutdown HTTP server
    httpd.shutdown()
    httpd.server_close()

    # Terminate
    registration_server.stop(None)
    registration_thread.join()
    kv_server.stop(None)
    kv_thread.join()

    LOG.info("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--categories", nargs="*", type=str)
    parser.add_argument(
        "--ca-out",
        type=str,
        help="Path where server's CA should be written",
        default="server_cert.pem",
    )
    args = parser.parse_args()

    if args.categories:
        categories = args.categories
    else:
        categories = DEFAULT_DISPATCH_CATEGORIES

    serve(args.ca_out, categories)
