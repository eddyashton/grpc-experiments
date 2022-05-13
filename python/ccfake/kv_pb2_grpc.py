# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import kv_pb2 as kv__pb2


class KVStub(object):
    """Approximation of CCF's KV interface
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Ready = channel.unary_unary(
                '/ccfake.KV/Ready',
                request_serializer=kv__pb2.ReadyRequest.SerializeToString,
                response_deserializer=kv__pb2.BeginTx.FromString,
                )
        self.Get = channel.unary_unary(
                '/ccfake.KV/Get',
                request_serializer=kv__pb2.GetRequest.SerializeToString,
                response_deserializer=kv__pb2.GetResponse.FromString,
                )
        self.Put = channel.unary_unary(
                '/ccfake.KV/Put',
                request_serializer=kv__pb2.PutRequest.SerializeToString,
                response_deserializer=kv__pb2.PutResponse.FromString,
                )
        self.ApplyTx = channel.unary_unary(
                '/ccfake.KV/ApplyTx',
                request_serializer=kv__pb2.ApplyRequest.SerializeToString,
                response_deserializer=kv__pb2.ApplyResponse.FromString,
                )


class KVServicer(object):
    """Approximation of CCF's KV interface
    """

    def Ready(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get(self, request, context):
        """Get a single key
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Put(self, request, context):
        """Put a single key-value pair
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ApplyTx(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_KVServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Ready': grpc.unary_unary_rpc_method_handler(
                    servicer.Ready,
                    request_deserializer=kv__pb2.ReadyRequest.FromString,
                    response_serializer=kv__pb2.BeginTx.SerializeToString,
            ),
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=kv__pb2.GetRequest.FromString,
                    response_serializer=kv__pb2.GetResponse.SerializeToString,
            ),
            'Put': grpc.unary_unary_rpc_method_handler(
                    servicer.Put,
                    request_deserializer=kv__pb2.PutRequest.FromString,
                    response_serializer=kv__pb2.PutResponse.SerializeToString,
            ),
            'ApplyTx': grpc.unary_unary_rpc_method_handler(
                    servicer.ApplyTx,
                    request_deserializer=kv__pb2.ApplyRequest.FromString,
                    response_serializer=kv__pb2.ApplyResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ccfake.KV', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class KV(object):
    """Approximation of CCF's KV interface
    """

    @staticmethod
    def Ready(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ccfake.KV/Ready',
            kv__pb2.ReadyRequest.SerializeToString,
            kv__pb2.BeginTx.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Get(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ccfake.KV/Get',
            kv__pb2.GetRequest.SerializeToString,
            kv__pb2.GetResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Put(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ccfake.KV/Put',
            kv__pb2.PutRequest.SerializeToString,
            kv__pb2.PutResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ApplyTx(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ccfake.KV/ApplyTx',
            kv__pb2.ApplyRequest.SerializeToString,
            kv__pb2.ApplyResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)