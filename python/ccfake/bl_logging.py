from loguru import logger as LOG
import argparse
import json

import grpc

import kv_pb2
import kv_pb2_grpc

PRIVATE_LOGGING_TABLE = "log_entries"


def handle_get_log(body, stub):
    params = json.loads(body)
    key = json.dumps(params["id"]).encode()
    LOG.trace("Getting log message")
    get_response = stub.Get(
        kv_pb2.GetRequest(
            table=PRIVATE_LOGGING_TABLE,
            key=key,
        )
    )

    if get_response.HasField("value"):
        result_code = 200
        result_body = get_response.value
    else:
        result_code = 204
        result_body = b''

    stub.ApplyTx(kv_pb2.ApplyRequest(code=result_code, body=result_body))


def handle_post_log(body, stub):
    params = json.loads(body)
    key = json.dumps(params["id"]).encode()
    value = params["msg"].encode()
    LOG.trace("Post log message")
    put_response = stub.Put(
        kv_pb2.PutRequest(
            table=PRIVATE_LOGGING_TABLE,
            key=key,
            value=value,
        )
    )
    existed = put_response.existed

    result_code = 200
    result_body = json.dumps(existed).encode()

    stub.ApplyTx(kv_pb2.ApplyRequest(code=result_code, body=result_body))


def handle_begin_tx(begin_tx, stub):
    if begin_tx.uri == "GET /app/log":
        handle_get_log(begin_tx.body, stub)
    elif begin_tx.uri == "POST /app/log":
        handle_post_log(begin_tx.body, stub)
    else:
        print(ValueError(f"Unhandled URI: {begin_tx.uri}"))
        stub.ApplyTx(
            kv_pb2.ApplyRequest(
                code=404, body=f"The URI {begin_tx.uri} is not handled".encode()
            )
        )


def run(ca, privk, cert):
    creds = grpc.ssl_channel_credentials(ca, privk, cert)

    with grpc.secure_channel("localhost:50052", creds) as channel:
        stub = kv_pb2_grpc.KVStub(channel)

        response = stub.Ready(kv_pb2.ReadyRequest())
        for begin_tx in response:
            LOG.trace("Handling transaction")
            handle_begin_tx(begin_tx, stub)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ca",
        type=str,
        help="Path to cert/roots to verify KV server",
        default="server_cert.pem",
    )
    parser.add_argument(
        "--cert",
        type=str,
        help="Path to certificate used for client auth",
        default="executor_cert.pem",
    )
    parser.add_argument(
        "--key",
        type=str,
        help="Path to private key used for client auth",
        default="executor_privk.pem",
    )
    args = parser.parse_args()

    with open(args.ca, "rb") as f:
        ca = f.read()
    with open(args.cert, "rb") as f:
        cert = f.read()
    with open(args.key, "rb") as f:
        privk = f.read()

    run(ca, privk, cert)
