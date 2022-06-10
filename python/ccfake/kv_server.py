from collections import defaultdict
from concurrent import futures
from enum import Enum
from threading import Thread
from loguru import logger as LOG

import argparse
import grpc

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
    def __init__(self):
        self.state = ExecutorState.Registered


class Registry(registry_pb2_grpc.RegistryServicer):
    def __init__(self, categories):
        self.executors = {category: {} for category in categories}

    def Register(self, request, context):
        ret = registry_pb2.RegisterResponse()
        if request.dispatch_category not in self.executors:
            ret.accepted = False
            allowed_s = "\n".join(self.executors.keys())
            ret.error = f"'{request.dispatch_category}' is not a known dispatch category.\nAllowed categories are:\n{allowed_s}"

        executors_for_category = self.executors[request.dispatch_category]
        if request.executor_ident in executors_for_category:
            ret.accepted = False
            ret.error = f"Executor with this identity is already registered. Identity is:\n{request.executor_ident}"
        else:
            executors_for_category[request.executor_ident] = Executor()
            ret.accepted = True

        return ret


class KV(kv_pb2_grpc.KVServicer):
    def __init__(self):
        self.kv = defaultdict(dict)
        self.available_clients = []

    def Get(self, request, context):
        ret = kv_pb2.GetResponse()
        table = self.kv[request.table]
        if request.key in table:
            ret.value = table[request.key]
        return ret

    def Put(self, request, context):
        table = self.kv[request.table]
        exists = request.key in table
        table[request.key] = request.value
        return kv_pb2.PutResponse(existed=exists)


def encode_accepted_client_certs(registry):
    # TODO: Constructing this on every session is unnecessarily expensive
    certs = b"\n".join(
        ident
        for cat, executors in registry.executors.items()
        for ident, _ in executors.items()
    )
    return certs


def fetch_server_cert_config(server_ident, registry):
    def fn():
        server_credentials = grpc.ssl_server_certificate_configuration(
            server_ident, encode_accepted_client_certs(registry)
        )
        return server_credentials

    return fn


def serve(categories):
    LOG.info("Registering workers in the following categories:")
    for cat in categories:
        LOG.info(f"  {cat}")

    # Generate a fresh key-pair. Write public cert to disk
    key_priv_pem, _ = crypto.generate_rsa_keypair(2048)
    cert_pem = crypto.generate_cert(key_priv_pem, cn="localhost", ca=True)
    server_cert_path = "server_cert.pem"
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
    kv = KV()
    kv_pb2_grpc.add_KVServicer_to_server(kv, kv_server)
    dynamic_creds = grpc.dynamic_ssl_server_credentials(
        grpc.ssl_server_certificate_configuration(server_ident),
        fetch_server_cert_config(server_ident, registry),
        True,
    )
    kv_server_address = "localhost:50052"
    LOG.info(f"Listening for KV traffic on {kv_server_address}")
    kv_server.add_secure_port(kv_server_address, dynamic_creds)

    # Listen on both servers
    kv_thread = Thread(target=lambda: kv_server.start())
    kv_thread.start()
    registration_server.start()

    LOG.info("Running...")

    # Terminate
    registration_server.wait_for_termination()
    kv_server.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--categories", nargs="*", type=str)
    args = parser.parse_args()

    if args.categories:
        categories = args.categories
    else:
        categories = DEFAULT_DISPATCH_CATEGORIES

    serve(categories)
