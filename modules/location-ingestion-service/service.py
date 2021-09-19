import json
import logging
import os

from geoalchemy2.functions import ST_Point
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Location

BOOTSTRAP_SERVER = os.environ.get("BOOTSTRAP_SERVER", "localhost:9092")
TOPIC_NAME = os.environ.get("TOPIC_NAME", "locations")

DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("location-ingestion-service")

class LocationIngestionService:
    def __init__(self) -> None:
        db_engine = create_engine(f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        Session = sessionmaker(bind=db_engine)
        self.session = Session()
    
    def save_location(self, location_data):
        new_location = Location()
        new_location.person_id = location_data["person_id"]
        new_location.creation_time = location_data["creation_time"]
        new_location.coordinate = ST_Point(location_data["latitude"], location_data["longitude"])
        self.session.add(new_location)
        self.session.commit()
        logger.info(f"Location detail created for person with id {new_location.person_id}")


def init_kafka_topic():
    admin_client = KafkaAdminClient(
        bootstrap_servers=BOOTSTRAP_SERVER
    )
    topics = admin_client.list_topics()
    if TOPIC_NAME in topics:
        logger.info(f"Skipping topic creation,  as topic '{TOPIC_NAME}' already present")
        return
    topic_list = []
    topic_list.append(NewTopic(name=TOPIC_NAME, num_partitions=1, replication_factor=1))
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
    logger.info(f"Topic '{TOPIC_NAME}' created")

def get_kafka_consumer():
    init_kafka_topic()
    consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=BOOTSTRAP_SERVER)
    return consumer

def main():
    '''
    Recieve the message in below format:
    {"person_id": 420,"creation_time": "2021-09-05T17:42:59.787Z","latitude": 36.0,"longitude": 126.0}
    '''
    logger.info(f"Starting Location Injection Service")
    service = LocationIngestionService()
    location_consumer = get_kafka_consumer()
    for loc_data in location_consumer:
        logger.debug(f"Received a message for processing: {loc_data}")
        location_data = json.loads(loc_data.value)
        logger.debug(f"Location message received: {location_data}")
        service.save_location(location_data)
        
if __name__ == '__main__':
    main()
