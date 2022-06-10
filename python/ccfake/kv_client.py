import grpc


import kv_pb2
import kv_pb2_grpc


def run():
    with grpc.insecure_channel("localhost:50052") as channel:
        stub = kv_pb2_grpc.KVStub(channel)

        table = "foo"
        key = b"\x42"

        print("----")
        response = stub.Get(kv_pb2.GetRequest(table=table, key=key))
        print(response)
        print(response.HasField("value"))
        print(response.value)

        print("----")
        response = stub.Put(kv_pb2.PutRequest(table=table, key=key, value=b"0x00"))
        print(response)
        print(response.existed)

        print("----")
        response = stub.Get(kv_pb2.GetRequest(table=table, key=key))
        print(response)
        print(response.HasField("value"))
        print(response.value)

        print("----")
        response = stub.Put(kv_pb2.PutRequest(table=table, key=key, value=b"0x01"))
        print(response)
        print(response.existed)

        print("----")
        response = stub.Get(kv_pb2.GetRequest(table=table, key=key))
        print(response)
        print(response.HasField("value"))
        print(response.value)


if __name__ == "__main__":
    run()
