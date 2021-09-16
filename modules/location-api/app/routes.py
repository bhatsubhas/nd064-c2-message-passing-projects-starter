def register_routes(api, app, root="api"):
    from app.location import register_routes as attach_location

    # Add routes
    attach_location(api, app)
