from loguru import logger as LOG
import argparse
import hashlib

import grpc

import registry_pb2
import registry_pb2_grpc

import crypto


def register(args, cert):
    with open(args.ca, "rb") as f:
        creds = grpc.ssl_channel_credentials(f.read())

    with grpc.secure_channel("localhost:50051", creds) as channel:
        stub = registry_pb2_grpc.RegistryStub(channel)

        LOG.info("----")
        response = stub.Register(
            registry_pb2.RegisterRequest(
                executor_ident=cert, dispatch_category=args.category
            )
        )
        LOG.info(response)
        LOG.info(response.accepted)
        LOG.info(response.error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ca",
        type=str,
        help="Path to cert/roots to verify registration server",
        default="server_cert.pem",
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Category to register new executor under",
        default="foo",
    )
    parser.add_argument(
        "--cert",
        type=str,
        help="Path where new executor's certificate should be written",
        default="executor_cert.pem",
    )
    parser.add_argument(
        "--key",
        type=str,
        help="Path where new executor's key should be written",
        default="executor_privk.pem",
    )
    args = parser.parse_args()

    # Generate a fresh key-pair and cert, write to disk
    key_priv_pem, key_pub_pem = crypto.generate_rsa_keypair(2048)
    # NB: Give each a unique CN
    cert_pem = crypto.generate_cert(
        key_priv_pem, cn=f"executor {hashlib.md5(key_pub_pem).hexdigest()}"
    )
    with open(args.cert, "wb") as f:
        f.write(cert_pem)
        LOG.info(f"Wrote executor's certificate to {args.cert}")
    with open(args.key, "wb") as f:
        f.write(key_priv_pem)
        LOG.info(f"Wrote executor's key to {args.key}")

    register(args, cert_pem)
