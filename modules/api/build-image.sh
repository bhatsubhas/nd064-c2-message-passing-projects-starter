#!/usr/bin/env bash

docker image build -t udaconnect-api:latest .
docker image tag udaconnect-api:latest bhatsubhas/udaconnect-api:latest
docker image push bhatsubhas/udaconnect-api:latest