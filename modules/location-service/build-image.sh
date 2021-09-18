#!/usr/bin/env bash

docker image build -t location-service:latest .
docker image tag location-service:latest bhatsubhas/location-service:latest
docker image push bhatsubhas/location-service:latest