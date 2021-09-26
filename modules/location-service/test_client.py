from sys import argv

import grpc
import datetime
import location_pb2
import location_pb2_grpc

channel = grpc.insecure_channel("localhost:5001")
stub = location_pb2_grpc.LocationServiceStub(channel)

get_request = location_pb2.GetLocationRequest(location_id=36)
get_response = stub.GetLocation(get_request)
print(f"Got location from DB - {get_response}")


list_request = location_pb2.ListExposedLocationsRequest(
    person_id=1,
    start_date=datetime.datetime.strptime("2020-01-01", "%Y-%m-%d").isoformat(),
    end_date=datetime.datetime.strptime("2020-12-31", "%Y-%m-%d").isoformat(),
    meters=5
)
list_response = stub.ListExposedLocations(list_request)
print(f"Received {len(list_response.locations)} records in response")
for location in list_response.locations:
    print(location)
    print("----------------------------------")

create_request = location_pb2.CreateLocationRequest(
    person_id=1,
    longitude="123.0",
    latitude="33.0",
    creation_time=datetime.datetime.now().isoformat()
)
create_response = stub.CreateLocation(create_request)
print(f"Created location entry in DB - {create_response}")
