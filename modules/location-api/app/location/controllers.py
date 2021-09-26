import json
import os

import location_pb2
from app.location.models import Location
from app.location.schemas import LocationSchema
from flask import g, request
from flask_restx import Namespace, Resource, fields

DATE_FORMAT = "%Y-%m-%d"

api = Namespace("Location", description="Location API for Udaconnect")  # noqa

location_request = api.model('LocationRequest', {
    'person_id': fields.Integer(required=True, description='Unique identifier of the person whose location information is being returned', example=20),
    'creation_time': fields.DateTime(required=True, description='Timestamp at which location detail was captured'),
    'longitude': fields.String(required=True, description='Longitude of the location'),
    'latitude': fields.String(required=True, description='Lattitude of the location')
})

location_response = api.model('LocationResponse', {
    'person_id': fields.Integer(readonly=True, description='Unique identifier of the person whose location information is being returned', example=20),
    'id': fields.Integer(readonly=True, description='Unique identifier of the location', example=101),
    'longitude': fields.String(required=True, description='Longitude of the location'),
    'latitude': fields.String(required=True, description='Lattitude of the location'),
    'creation_time': fields.DateTime(required=True, description='Timestamp at which location detail was captured')
})

success_response = api.model('SuccessResponse', {
    'message': fields.String(required=True, description='Request Accepted')
})
# TODO: This needs better exception handling

@api.route("/locations/<int:location_id>")
@api.param("location_id", "Unique ID for a given Location", _in="query")
class LocationRetrieveResource(Resource):
    @api.doc("Get location when unique ID is passed")
    @api.marshal_with(location_response)
    def get(self, location_id) -> Location:
        location_request = location_pb2.GetLocationRequest(location_id=location_id)
        location_response = g.location_stub.GetLocation(location_request)
        return {
            "person_id": location_response.person_id,
            "id": location_response.location_id,
            "longitude": location_response.longitude,
            "latitude": location_response.latitude,
            "creation_time": location_response.creation_time
        }, 200

@api.route("/locations")
class LocationCreateResource(Resource):
    @api.doc("Create a location entry when details are passed")
    @api.expect(location_request)
    @api.marshal_with(success_response, code=202)
    def post(self) -> Location:
        location_data = request.get_json()
        create_location_request = location_pb2.CreateLocationRequest(
            person_id=location_data["person_id"],
            creation_time=location_data["creation_time"],
            longitude=location_data["longitude"],
            latitude=location_data["latitude"]
        )
        create_location_response = g.location_stub.CreateLocation(create_location_request)
        return {
            "message" : create_location_response.message
        }, 202
