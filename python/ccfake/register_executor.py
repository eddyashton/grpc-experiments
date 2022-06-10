import grpc

import sys

import registry_pb2
import registry_pb2_grpc


def register(executor_ident, category):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = registry_pb2_grpc.RegistryStub(channel)

        print("----")
        response = stub.Register(
            registry_pb2.RegisterRequest(
                executor_ident=executor_ident, dispatch_category=category
            )
        )
        print(response)
        print(response.accepted)
        print(response.error)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("Missing argument at position 0: executor_ident")

    executor_ident = open(sys.argv[1], mode="rb").read()

    if len(sys.argv) < 3:
        raise ValueError("Missing argument at position 1: category")

    category = sys.argv[2]

    register(executor_ident, category)
