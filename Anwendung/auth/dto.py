from flask_restx import Namespace, fields


class AuthDto:
    auth_ns = Namespace("auth", description="Authenticate and receive tokens.")

    user_obj = auth_ns.model(
        "User object",
        {
            "email": fields.String,
            "name": fields.String,
            "username": fields.String,
            "joined_date": fields.DateTime,
            "role_id": fields.Integer,
        },
    )

    auth_login = auth_ns.model(
        "Login data",
        {
            "email": fields.String(required=True),
            "password": fields.String(required=True),
        },
    )

    auth_register = auth_ns.model(
        "Registration data",
        {
            "email": fields.String(required=True),
            "username": fields.String(required=True),
            # Name is optional
            "name": fields.String,
            "password": fields.String(required=True),
        },
    )

    auth_success = auth_ns.model(
        "Auth success response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "access_token": fields.String,
            "user": fields.Nested(user_obj),
        },
    )