#!/usr/bin/env bash

python -m grpc_tools.protoc -I=./protos --python_out=./ --grpc_python_out=./ location.proto

cp location_pb2.py location_pb2_grpc.py ../location-api
cp location_pb2.py location_pb2_grpc.py ../api
