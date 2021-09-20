from datetime import datetime

from app.udaconnect.models import Person
from app.udaconnect.services import ConnectionService, PersonService
from flask import request
from flask_restx import Namespace, Resource, fields
from typing import Optional, List

DATE_FORMAT = "%Y-%m-%d"

api = Namespace("UdaConnect", description="Connections via geolocation.")  # noqa

# Request and Response models
person = api.model('Person', {
    'id': fields.Integer(readonly=True, description='Unique identifier of the person',example=101),
    'first_name': fields.String(required=True, description='First name of the person', example='John'), 
    'last_name': fields.String(required=True, description='Last name of the person', example='Doe'),
    'company_name': fields.String(required=True, description='Company to which person belongs to', example='The ABCD Inc.')
})
location = api.model('Location', {
    'person_id': fields.Integer(readonly=True, description='Unique identifier of the person whose location information is being returned', example=20),
    'id': fields.Integer(readonly=True, description='Unique identifier of the location', example=101),
    'longitude': fields.String(required=True, description='Longitude of the location'),
    'latitude': fields.String(required=True, description='Lattitude of the location'),
    'creation_time': fields.DateTime(required=True, description='Timestamp at which location detail was captured')
})
connection = api.model('Connection', {
    'location': fields.Nested(location),
    'person': fields.Nested(person)
})


# TODO: This needs better exception handling

@api.route("/persons")
class PersonsResource(Resource):
    @api.expect(person)
    @api.marshal_with(person, code=201)
    def post(self) -> Person:
        payload = request.get_json()
        new_person: Person = PersonService.create(payload)
        return new_person, 201

    @api.marshal_list_with(person)
    def get(self) -> List[Person]:
        persons: List[Person] = PersonService.retrieve_all()
        return persons


@api.route("/persons/<person_id>")
@api.param("person_id", "Unique ID for a given Person", _in="query")
class PersonResource(Resource):
    @api.doc("Get location when unique ID is passed")
    @api.marshal_list_with(person)
    def get(self, person_id) -> Person:
        person: Person = PersonService.retrieve(person_id)
        return person


@api.route("/persons/<int:person_id>/connection")
@api.param("person_id", "Unique ID for a given Person")
@api.param("start_date", "Lower bound of date range in YYYY-MM-DD format", _in="query", required=True)
@api.param("end_date", "Upper bound of date range in YYYY-MM-DD format", _in="query", required=True)
@api.param("distance", "Proximity to a given user in meters", _in="query")
class ConnectionDataResource(Resource):
    @api.marshal_list_with(connection)
    def get(self, person_id):
        start_date: datetime = datetime.strptime(request.args["start_date"], DATE_FORMAT)
        end_date: datetime = datetime.strptime(request.args["end_date"], DATE_FORMAT)
        distance: Optional[int] = request.args.get("distance", 5)

        results = ConnectionService.find_contacts(
            person_id=person_id,
            start_date=start_date,
            end_date=end_date,
            meters=distance,
        )
        return results
