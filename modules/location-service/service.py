import logging
import os
import time
from datetime import datetime, timedelta
from concurrent import futures
from typing import List, Optional

import grpc
from geoalchemy2.functions import ST_Point
from sqlalchemy import create_engine
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
GRPC_SERVER = os.environ["LOCATION_GRPC_SERVER"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("location-service")
db_engine = create_engine(f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
Session = sessionmaker(bind=db_engine)
session = Session()


class LocationServicer(location_pb2_grpc.LocationServiceServicer):
    
    def CreateLocation(self, request, context):
        new_location = Location()
        new_location.person_id = request.person_id
        new_location.creation_time = datetime.fromisoformat(request.creation_time)
        new_location.coordinate = ST_Point(request.latitude, request.longitude)
        session.add(new_location)
        session.commit()
        logger.info(f"[CreateLocation] Created Location entry for person with id {new_location.person_id}")
        return location_pb2.Location(
            location_id=new_location.id,
            person_id=new_location.person_id,
            longitude=new_location.longitude,
            latitude=new_location.latitude,
            creation_time=new_location.creation_time.isoformat()
        )

    def GetLocation(self, request, context):
        location_id = request.location_id
        location, coord_text = (
            session.query(Location, Location.coordinate.ST_AsText())
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

    def ListLocations(self, request, context):
        start_date: datetime = datetime.fromisoformat(request.start_date)
        end_date: datetime = datetime.fromisoformat(request.end_date)

        locations: List = session.query(Location).filter(
            Location.person_id == request.person_id
        ).filter(Location.creation_time < end_date).filter(
            Location.creation_time >= start_date
        ).all()

        listLocationsResponse = location_pb2.ListLocationsResponse()
        for location in locations:
            loc = location_pb2.Location(
                location_id=location.id,
                person_id=location.person_id,
                longitude=location.longitude,
                latitude=location.latitude,
                creation_time=location.creation_time.isoformat()
            )
            listLocationsResponse.locations.append(loc)
        logger.info(f"[ListLocations] Returning Locations list for person id {request.person_id} between {start_date} and {end_date}")
        logger.info(f"[ListLocations] {len(listLocationsResponse.locations)} location(s) found")
        return listLocationsResponse




def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    location_pb2_grpc.add_LocationServiceServicer_to_server(LocationServicer(), server)

    logger.info(f"Location Service is starting on {GRPC_SERVER}...")
    server.add_insecure_port(GRPC_SERVER)
    server.start()

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    main()




