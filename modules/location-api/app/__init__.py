import os

import grpc
import location_pb2_grpc
from flask import Flask, g, jsonify
from flask_cors import CORS
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from kafka import KafkaProducer

db = SQLAlchemy()

def create_app(env=None):
    from app.config import config_by_name
    from app.routes import register_routes

    app = Flask(__name__)
    app.config.from_object(config_by_name[env or "test"])
    api = Api(app, title="Location API", version="0.1.0")

    CORS(app)  # Set CORS for development

    register_routes(api, app)
    db.init_app(app)

    @app.route("/health")
    def health():
        return jsonify("healthy")

    @app.before_request
    def before_request():
        # Set up a Kafka producer
        KAFKA_SERVER = os.environ["BOOTSTRAP_SERVER"]
        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
        # Setting Kafka to g enables us to use this
        # in other parts of our application
        g.kafka_producer = producer

        # Setup gRPC Client Stub
        GRPC_SERVER = os.environ["LOCATION_GRPC_SERVER"]
        channel = grpc.insecure_channel(GRPC_SERVER)
        stub = location_pb2_grpc.LocationRetrieveServiceStub(channel)
        g.grpc_stub = stub

    return app
