import logging
from datetime import datetime
from typing import Dict, List

import location_pb2
from app import db
from app.udaconnect.models import Connection, Location, Person
from flask import g

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")


class ConnectionService:
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime, end_date: datetime, meters=5
    ) -> List[Connection]:
        """
        Finds all Person who have been within a given distance of a given Person within a date range.

        This will run rather quickly locally, but this is an expensive method and will take a bit of time to run on
        large datasets. This is by design: what are some ways or techniques to help make this data integrate more
        smoothly for a better user experience for API consumers?
        """
        # Instead of DB Call use gRPC call to get the exposed locations
        location_list_request = location_pb2.ListExposedLocationsRequest(
            person_id=person_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            meters=int(meters)
        )
        location_list_response = g.location_stub.ListExposedLocations(location_list_request)
        exposed_locations = location_list_response.locations

        # Cache all users in memory for quick lookup
        person_map: Dict[str, Person] = {person.id: person for person in PersonService.retrieve_all()}
        result: List[Connection] = []
        for exposed_loc in exposed_locations:
                location = Location(
                    id=exposed_loc.location_id,
                    person_id=exposed_loc.exposed_person_id,
                    creation_time=datetime.fromisoformat(exposed_loc.exposed_time)
                )
                location.set_wkt_with_coords(exposed_loc.exposed_lat, exposed_loc.exposed_long)

                result.append(
                    Connection(
                        person=person_map[exposed_loc.exposed_person_id], 
                        location=location
                    )
                )

        return result

class PersonService:
    @staticmethod
    def create(person: Dict) -> Person:
        new_person = Person()
        new_person.first_name = person["first_name"]
        new_person.last_name = person["last_name"]
        new_person.company_name = person["company_name"]

        db.session.add(new_person)
        db.session.commit()

        return new_person

    @staticmethod
    def retrieve(person_id: int) -> Person:
        person = db.session.query(Person).get(person_id)
        return person

    @staticmethod
    def retrieve_all() -> List[Person]:
        return db.session.query(Person).all()
