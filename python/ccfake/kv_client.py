from loguru import logger as LOG
import argparse

import grpc

import kv_pb2
import kv_pb2_grpc


def run(ca, privk, cert):
    creds = grpc.ssl_channel_credentials(ca, privk, cert)

    with grpc.secure_channel("localhost:50052", creds) as channel:
        stub = kv_pb2_grpc.KVStub(channel)

        LOG.info("----")
        response = stub.Ready(kv_pb2.ReadyRequest())
        LOG.info(response)

        table = "foo"
        key = b"\x42"

        LOG.info("----")
        response = stub.Get(kv_pb2.GetRequest(table=table, key=key))
        LOG.info(response)
        LOG.info(response.HasField("value"))
        LOG.info(response.value)

        LOG.info("----")
        response = stub.Put(kv_pb2.PutRequest(table=table, key=key, value=b"0x00"))
        LOG.info(response)
        LOG.info(response.existed)

        LOG.info("----")
        response = stub.Get(kv_pb2.GetRequest(table=table, key=key))
        LOG.info(response)
        LOG.info(response.HasField("value"))
        LOG.info(response.value)

        LOG.info("----")
        response = stub.Put(kv_pb2.PutRequest(table=table, key=key, value=b"0x01"))
        LOG.info(response)
        LOG.info(response.existed)

        LOG.info("----")
        response = stub.Get(kv_pb2.GetRequest(table=table, key=key))
        LOG.info(response)
        LOG.info(response.HasField("value"))
        LOG.info(response.value)

        LOG.info("----")
        response = stub.ApplyTx(kv_pb2.ApplyRequest())
        LOG.info(response)


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
