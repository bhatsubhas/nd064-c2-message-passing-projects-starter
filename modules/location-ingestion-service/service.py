import json
import logging
import os

from geoalchemy2.functions import ST_Point
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Location

DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
KAFKA_HOST = os.environ.get("KAFKA_HOST", "localhost")
KAFKA_PORT = os.environ.get("KAFKA_PORT", 9092)
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "locations")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("location-ingestion-service")

class LocationIngestionService:
    def __init__(self) -> None:
        self.bootstrap_server = f"{KAFKA_HOST}:{KAFKA_PORT}"
        self.__init_db_session()
        self.__init_topic()
        self.location_receiver = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=self.bootstrap_server)

    def __init_db_session(self):
        db_engine = create_engine(f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        Session = sessionmaker(bind=db_engine)
        self.session = Session()

    def __init_topic(self):
        admin_client = KafkaAdminClient(
            bootstrap_servers=self.bootstrap_server
        )
        topics = admin_client.list_topics()
        if KAFKA_TOPIC in topics:
            logger.info(f"Skipping topic creation,  as topic '{KAFKA_TOPIC}' already present")
            return
        topic_list = []
        topic_list.append(NewTopic(name=KAFKA_TOPIC, num_partitions=1, replication_factor=1))
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        logger.info(f"Topic '{KAFKA_TOPIC}' created")
    
    def ingest_locations(self):
        '''
        Recieve the message in below format:
        {"person_id": 420,"creation_time": "2021-09-05T17:42:59.787Z","latitude": 36.0,"longitude": 126.0}
        '''
        for loc_data in self.location_receiver:
            logger.debug(f"Received a location message for ingestion: {loc_data}")
            location_data = json.loads(loc_data.value)
            self.save_location(location_data)
            
    def save_location(self, location_data):
        logger.debug(f"Saving Location message to db: {location_data}")
        new_location = Location()
        new_location.person_id = location_data["person_id"]
        new_location.creation_time = location_data["creation_time"]
        new_location.coordinate = ST_Point(location_data["latitude"], location_data["longitude"])
        self.session.add(new_location)
        self.session.commit()
        logger.info(f"Location detail saved for person with id {new_location.person_id}")


def main():
    logger.info(f"Starting Location Ingestion Service")
    service = LocationIngestionService()
    service.ingest_locations()
        
if __name__ == '__main__':
    main()
