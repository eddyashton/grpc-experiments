from concurrent import futures
from collections import defaultdict

import grpc

import ccfake_pb2
import ccfake_pb2_grpc


class KV(ccfake_pb2_grpc.KVServicer):
    def __init__(self):
        self.kv = defaultdict(dict)
        self.available_clients = []

    def Get(self, request, context):
        ret = ccfake_pb2.GetResponse()
        table = self.kv[request.table]
        if request.key in table:
            ret.value = table[request.key]
        return ret

    def Put(self, request, context):
        table = self.kv[request.table]
        exists = request.key in table
        table[request.key] = request.value
        return ccfake_pb2.PutResponse(existed=exists)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ccfake_pb2_grpc.add_KVServicer_to_server(KV(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
