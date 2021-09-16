import logging
import os
import time
from concurrent import futures

import grpc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import person_pb2
import person_pb2_grpc
from models import Person

DATE_FORMAT = "%Y-%m-%d"
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
GRPC_SERVER = os.environ["PERSON_GRPC_SERVER"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("person-service")
db_engine = create_engine(f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
Session = sessionmaker(bind=db_engine)
session = Session()


class PersonServicer(person_pb2_grpc.PersonServiceServicer):
    
    def CreatePerson(self, request, context):
        new_person = Person()
        new_person.first_name = request.first_name
        new_person.last_name = request.last_name
        new_person.company_name = request.company_name
        session.add(new_person)
        session.commit()
        logger.info(f"[CreatePerson] Created entry for {new_person.first_name} in person table with id {new_person.id}")
        return person_pb2.Person(
            id=new_person.id,
            first_name=new_person.first_name,
            last_name=new_person.last_name,
            company_name=new_person.company_name
        )

    def GetPerson(self, request, context):
        person_id = request.person_id
        person = session.query(Person).get(person_id)
        logger.info(f"[GetPerson] Returning Person record for person id {person.id}")
        return person_pb2.Person(
            id=person.id,
            first_name=person.first_name,
            last_name=person.last_name,
            company_name=person.company_name
        )

    def ListPersons(self, request, context):
        listPersonsResponse = person_pb2.ListPersonsResponse()
        for person in session.query(Person).all():
            listPersonsResponse.persons.append(
                person_pb2.Person(
                    id=person.id,
                    first_name=person.first_name,
                    last_name=person.last_name,
                    company_name=person.company_name
                )
            )
        logger.info(f"[ListPersons] Returning {len(listPersonsResponse.persons)} record(s)")
        return listPersonsResponse

def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    person_pb2_grpc.add_PersonServiceServicer_to_server(PersonServicer(), server)

    logger.info(f"Person Service is starting on port {GRPC_SERVER}...")
    server.add_insecure_port(GRPC_SERVER)
    server.start()

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    main()




