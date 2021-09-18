#!/usr/bin/env bash

docker image build -t location-ingestion-service:latest .
docker image tag location-ingestion-service:latest bhatsubhas/location-ingestion-service:latest
docker image push bhatsubhas/location-ingestion-service:latest