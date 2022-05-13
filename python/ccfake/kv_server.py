from concurrent import futures
from collections import defaultdict

import grpc

import registry_pb2
import registry_pb2_grpc

import kv_pb2
import kv_pb2_grpc

class Registry(registry_pb2_grpc.RegistryServicer):
    pass

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


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kv_pb2_grpc.add_KVServicer_to_server(KV(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
