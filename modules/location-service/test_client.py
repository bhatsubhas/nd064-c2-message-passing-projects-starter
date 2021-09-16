from sys import argv

import grpc
import datetime
import location_pb2
import location_pb2_grpc

channel = grpc.insecure_channel("localhost:5005")
stub = location_pb2_grpc.LocationServiceStub(channel)

get_request = location_pb2.GetLocationRequest(location_id=36)
get_response = stub.GetLocation(get_request)
print(f"Got location from DB - {get_response}")


list_request = location_pb2.ListLocationsRequest(
    person_id=1,
    start_date=datetime.datetime.strptime("2021-09-01", "%Y-%m-%d").isoformat(),
    end_date=datetime.datetime.strptime("2021-09-30", "%Y-%m-%d").isoformat()
)
list_response = stub.ListLocations(list_request)
print(f"Received {len(list_response.locations)} records in response")
for location in list_response.locations:
    print(location)
    print("----------------------------------")

create_request = location_pb2.CreateLocationRequest(
    person_id=1,
    longitude="123",
    latitude="32",
    creation_time=datetime.datetime.now().isoformat()
)
create_response = stub.CreateLocation(create_request)
print(f"Created location entry in DB - {create_response}")