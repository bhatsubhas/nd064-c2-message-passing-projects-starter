from sys import argv

import grpc
import datetime
import person_pb2
import person_pb2_grpc

channel = grpc.insecure_channel("localhost:5005")
stub = person_pb2_grpc.PersonServiceStub(channel)

person_request = person_pb2.CreatePersonRequest(
    first_name="Prakash",
    last_name="S",
    company_name="Broadero"
)
person_response = stub.CreatePerson(person_request)
print(f"Created {person_response}")

person_id = person_pb2.GetPersonRequest(person_id=12)
person_response = stub.GetPerson(person_id)
print(f"Got {person_response} for person_id 12")

empty = person_pb2.ListPersonsRequest()
personList = stub.ListPersons(empty)
print(f"Received {len(personList.persons)} records in response")
print("-----------------------------------------------")
for person in personList.persons:
    print(person)
    print("---------------------")