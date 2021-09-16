import logging
from typing import List

import person_pb2
from app.person.models import Person
from flask import g, request
from flask_restx import Namespace, Resource, fields

api = Namespace("Person", description="Person API for Udaconnect")  # noqa

person_request = api.model('PersonRequest', {
    'first_name': fields.String(required=True, description='First Name of the person', example="John"),
    'last_name': fields.String(required=True, description='Last Name of the person', example="Doe"),
    'company_name': fields.String(required=True, description='Company Name of the person', example="The ACME Inc")
})

person_response = api.model('PersonResponse', {
    'id': fields.Integer(required=True, description='Unique identifier of the person', example=20),
    'first_name': fields.String(required=True, description='First Name of the person', example="John"),
    'last_name': fields.String(required=True, description='Last Name of the person', example="Doe"),
    'company_name': fields.String(required=True, description='Company Name of the person', example="The ACME Inc")
})


# TODO: This needs better exception handling

@api.route("/persons")
class PersonsResource(Resource):
    @api.expect(person_request)
    @api.marshal_with(person_response, code=201)
    def post(self) -> Person:
        payload = request.get_json()
        
        create_person_request = person_pb2.CreatePersonRequest(
            first_name=payload["first_name"],
            last_name=payload["last_name"],
            company_name=payload["company_name"]
        )
        person_response = g.grpc_stub.CreatePerson(create_person_request)
        person = Person()
        person.id = person_response.id
        person.first_name=person_response.first_name
        person.last_name=person_response.last_name
        person.company_name=person_response.company_name
        return person, 201

    @api.marshal_list_with(person_response)
    def get(self) -> List[Person]:
        list_persons_request = person_pb2.ListPersonsRequest()
        person_list_response = g.grpc_stub.ListPersons(list_persons_request)
        person_list = []
        for person_response in person_list_response.persons:
            person = Person()
            person.id = person_response.id
            person.first_name=person_response.first_name
            person.last_name=person_response.last_name
            person.company_name=person_response.company_name
            person_list.append(person)
        return person_list


@api.route("/persons/<int:person_id>")
@api.param("person_id", "Unique ID for a given Person", _in="query")
class PersonResource(Resource):
    @api.marshal_with(person_response)
    def get(self, person_id) -> Person:
        get_person_request = person_pb2.GetPersonRequest(person_id=person_id)
        person_response = g.grpc_stub.GetPerson(get_person_request)
        person = Person()
        person.id = person_response.id
        person.first_name=person_response.first_name
        person.last_name=person_response.last_name
        person.company_name=person_response.company_name
        return person, 200
