import grpc


import kv_pb2
import kv_pb2_grpc


def run():
    with open("./cert.pem", "rb") as f:
        cert = f.read()
    with open("./key.pem", "rb") as f:
        key = f.read()
    creds = grpc.ssl_channel_credentials(cert, key, cert)

    with grpc.secure_channel("localhost:50052", creds) as channel:
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
