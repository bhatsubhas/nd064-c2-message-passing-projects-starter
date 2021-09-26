#!/usr/bin/env bash

docker image build -t udaconnect-app:latest .
docker image tag udaconnect-app:latest bhatsubhas/udaconnect-app:latest
docker image push bhatsubhas/udaconnect-app:latest