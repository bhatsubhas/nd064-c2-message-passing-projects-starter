#!/usr/bin/env bash

docker image build -t location-api:latest .
docker image tag location-api:latest bhatsubhas/location-api:latest
docker image push bhatsubhas/location-api:latest