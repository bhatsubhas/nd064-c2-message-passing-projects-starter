import json
import logging
import os
import time
from concurrent import futures
from datetime import datetime, timedelta
from typing import List

import grpc
from kafka import KafkaProducer
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker

import location_pb2
import location_pb2_grpc
from models import Location

DATE_FORMAT = "%Y-%m-%d"
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
KAFKA_TOPIC_NAME = os.environ.get("TOPIC_NAME", "locations")
KAFKA_SERVER = os.environ.get("BOOTSTRAP_SERVER", "localhost:9092")
LOCATION_GRPC_SERVER = os.environ.get("LOCATION_GRPC_SERVER", "localhost:5001")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("location-service")

class LocationServicer(location_pb2_grpc.LocationServiceServicer):

    def __init__(self):
        self.kafka_producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
        self.db_engine = create_engine(f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()


    def CreateLocation(self, request, context):
        location_data = {
            "person_id": request.person_id,
            "creation_time": request.creation_time,
            "latitude": request.latitude,
            "longitude": request.longitude
        }
        self.kafka_producer.send(KAFKA_TOPIC_NAME, json.dumps(location_data).encode())
        logger.info(f"[CreateLocation] Accepted Location entry for person with id {request.person_id}")
        return location_pb2.CreateLocationResponse(
            message="Accepted request to create location entry"
        )

    def GetLocation(self, request, context):
        location_id = request.location_id
        location, coord_text = (
            self.session.query(Location, Location.coordinate.ST_AsText())
            .filter(Location.id == location_id)
            .one()
        )

        # Rely on database to return text form of point to reduce overhead of conversion in app code
        location.wkt_shape = coord_text
        logger.info(f"[GetLocation] Returning Location record for location_id {location_id}")
        return location_pb2.Location(
            location_id=location.id,
            person_id=location.person_id,
            longitude=location.longitude,
            latitude=location.latitude,
            creation_time=location.creation_time.isoformat()
        )

    def ListExposedLocations(self, request, context):
        start_date: datetime = datetime.fromisoformat(request.start_date)
        end_date: datetime = datetime.fromisoformat(request.end_date)
        meters: int = request.meters

        locations: List = self.session.query(Location).filter(
            Location.person_id == request.person_id
        ).filter(Location.creation_time < end_date).filter(
            Location.creation_time >= start_date
        ).all()

        # Prepare arguments for queries
        data = []
        for location in locations:
            data.append(
                {
                    "person_id": request.person_id,
                    "longitude": location.longitude,
                    "latitude": location.latitude,
                    "meters": meters,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                }
            )

        query = text(
            """
        SELECT  person_id, id, ST_X(coordinate), ST_Y(coordinate), creation_time
        FROM    location
        WHERE   ST_DWithin(coordinate::geography,ST_SetSRID(ST_MakePoint(:latitude,:longitude),4326)::geography, :meters)
        AND     person_id != :person_id
        AND     TO_DATE(:start_date, 'YYYY-MM-DD') <= creation_time
        AND     TO_DATE(:end_date, 'YYYY-MM-DD') > creation_time;
        """
        )

        list_locations_response = location_pb2.ListExposedLocationsResponse()
        for line in tuple(data):
            for (
                exposed_person_id,
                location_id,
                exposed_lat,
                exposed_long,
                exposed_time,
            ) in self.db_engine.execute(query, **line):
                exposed_location = location_pb2.ExposedLocation(
                location_id=location_id,
                exposed_person_id=exposed_person_id,
                exposed_long=exposed_long,
                exposed_lat=exposed_lat,
                exposed_time=exposed_time.isoformat()
                )
                list_locations_response.locations.append(exposed_location)

        logger.info(f"[ListLocations] Returning Exposed Locations list for person id {request.person_id} between {start_date} and {end_date}")
        logger.info(f"[ListLocations] {len(list_locations_response.locations)} exposed location(s) found")
        return list_locations_response




def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    location_pb2_grpc.add_LocationServiceServicer_to_server(LocationServicer(), server)

    logger.info(f"Location Service is starting on {LOCATION_GRPC_SERVER}...")
    server.add_insecure_port(LOCATION_GRPC_SERVER)
    server.start()

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    main()




