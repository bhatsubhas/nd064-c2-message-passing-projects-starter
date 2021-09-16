from app.location.models import Connection, Location, Person  # noqa
from app.location.schemas import (ConnectionSchema, LocationSchema,  # noqa
                                  PersonSchema)


def register_routes(api, app, root="api"):
    from app.location.controllers import api as location_api

    api.add_namespace(location_api, path=f"/{root}")
