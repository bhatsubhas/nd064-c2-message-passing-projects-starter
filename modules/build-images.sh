docker image build -t person-api ./person-api
docker image tag person-api:latest bhatsubhas/person-api:latest
docker image push bhatsubhas/person-api:latest

docker image build -t person-service ./person-service
docker image tag person-service:latest bhatsubhas/person-service:latest
docker image push bhatsubhas/person-service:latest

docker image build -t location-api ./location-api
docker image tag location-api:latest bhatsubhas/location-api:latest
docker image push bhatsubhas/location-api:latest

docker image build -t location-ingestion-service:latest ./location-ingestion-service
docker image tag location-ingestion-service:latest bhatsubhas/location-ingestion-service:latest
docker image push bhatsubhas/location-ingestion-service:latest

# Need to work on below 3 services

docker image build -t location-service:latest ./location-service
docker image tag location-service:latest bhatsubhas/location-service:latest
docker image push bhatsubhas/location-service:latest

docker image build -t connections-api ./api
docker image tag connections-api:latest bhatsubhas/connections-api:latest
docker image push bhatsubhas/connections-api:latest

docker image build -t udaconnect-app ./frontend
docker image tag udaconnect-app:latest bhatsubhas/udaconnect-app:latest
docker image push bhatsubhas/udaconnect-app:latest