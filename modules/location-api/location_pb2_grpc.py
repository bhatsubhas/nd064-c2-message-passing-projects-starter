# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import location_pb2 as location__pb2


class LocationRetrieveServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RetrieveLocation = channel.unary_unary(
                '/LocationRetrieveService/RetrieveLocation',
                request_serializer=location__pb2.LocationRequest.SerializeToString,
                response_deserializer=location__pb2.LocationResponse.FromString,
                )
        self.RetrieveLocationList = channel.unary_unary(
                '/LocationRetrieveService/RetrieveLocationList',
                request_serializer=location__pb2.LocationListRequest.SerializeToString,
                response_deserializer=location__pb2.LocationResponseList.FromString,
                )


class LocationRetrieveServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RetrieveLocation(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RetrieveLocationList(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LocationRetrieveServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RetrieveLocation': grpc.unary_unary_rpc_method_handler(
                    servicer.RetrieveLocation,
                    request_deserializer=location__pb2.LocationRequest.FromString,
                    response_serializer=location__pb2.LocationResponse.SerializeToString,
            ),
            'RetrieveLocationList': grpc.unary_unary_rpc_method_handler(
                    servicer.RetrieveLocationList,
                    request_deserializer=location__pb2.LocationListRequest.FromString,
                    response_serializer=location__pb2.LocationResponseList.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'LocationRetrieveService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class LocationRetrieveService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RetrieveLocation(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/LocationRetrieveService/RetrieveLocation',
            location__pb2.LocationRequest.SerializeToString,
            location__pb2.LocationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RetrieveLocationList(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/LocationRetrieveService/RetrieveLocationList',
            location__pb2.LocationListRequest.SerializeToString,
            location__pb2.LocationResponseList.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
