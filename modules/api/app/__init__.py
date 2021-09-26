from flask import Flask, jsonify, g
from flask_cors import CORS
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
import location_pb2_grpc
import grpc
import os

db = SQLAlchemy()


def create_app(env=None):
    from app.config import config_by_name
    from app.routes import register_routes

    app = Flask(__name__)
    app.config.from_object(config_by_name[env or "test"])
    api = Api(app, title="UdaConnect API", version="0.1.0")

    CORS(app)  # Set CORS for development

    register_routes(api, app)
    db.init_app(app)

    @app.route("/health")
    def health():
        return jsonify("healthy")

    @app.before_request
    def before_request():
        # Setup gRPC Client Stub
        LOCATION_GRPC_HOST = os.environ.get("LOCATION_GRPC_HOST", "localhost")
        LOCATION_GRPC_PORT = os.environ.get("LOCATION_GRPC_PORT", "5001")
        channel = grpc.insecure_channel(f"{LOCATION_GRPC_HOST}:{LOCATION_GRPC_PORT}")
        g.location_stub = location_pb2_grpc.LocationServiceStub(channel)

    return app
