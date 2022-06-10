from loguru import logger as LOG
import argparse

import grpc

import registry_pb2
import registry_pb2_grpc

import crypto


def register(args, executor_ident):
    with open(args.server_cert, 'rb') as f:
        creds = grpc.ssl_channel_credentials(f.read())
    
    with grpc.secure_channel("localhost:50051", creds) as channel:
        stub = registry_pb2_grpc.RegistryStub(channel)

        print("----")
        response = stub.Register(
            registry_pb2.RegisterRequest(
                executor_ident=executor_ident, dispatch_category=args.category
            )
        )
        print(response)
        print(response.accepted)
        print(response.error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server-cert",
        type=str,
        help="Path to cert/roots to verify registration server",
        default="server_cert.pem"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Category to register new executor under",
        default="foo"
    )
    parser.add_argument(
        "--executor-cert",
        type=str,
        help="Path where new executor's certificate should be written",
        default="executor_cert.pem",
    )
    parser.add_argument(
        "--executor-key",
        type=str,
        help="Path where new executor's key should be written",
        default="executor_privk.pem",
    )
    args = parser.parse_args()

    # Generate a fresh key-pair and cert, write to disk
    key_priv_pem, _ = crypto.generate_rsa_keypair(2048)
    cert_pem = crypto.generate_cert(key_priv_pem, cn="executor")
    with open(args.executor_cert, "wb") as f:
        f.write(cert_pem)
        LOG.info(f"Wrote executor's certificate to {args.executor_cert}")
    with open(args.executor_key, "wb") as f:
        f.write(key_priv_pem)
        LOG.info(f"Wrote executor's key to {args.executor_key}")

    register(args, cert_pem)
