import os
from datetime import datetime
from flask import current_app
from flask_jwt_extended import create_access_token
from extensions import db
from database.models import UserSchema
from database.user import User

user_schema = UserSchema()

def message(status, message):
    response_object ={"status":status, "message":message}

def validation_error(status, errors):
    response_object = {"status": status, "errors": errors}

    return response_object


def err_resp(msg, reason, code):
    err = message(False, msg)
    err["err_reason"] = reason
    return err, code

def internal_err_resp():
    err = message(False, "Something went wrong during the process!")
    err["error_reason"] = "server_error"
    return err, 500


class AuthService:
    @staticmethod
    def login(data):
        username = data["username"]
        password = data["password"]

        try:
            if not (user := User.query.filter_by(username=username).first()):
                return err_resp(
                    "Username doesn't exist",
                    404
                )
            elif user and user.verify_password(password):
                user_info = user_schema.dump(user)
                access_token = create_access_token(identity=user.id)
                resp = message(True, "Successfully logged in")
                resp["access_token"] = access_token
                resp["user"] = user_info
                return resp, 200

            return err_resp(
            "Failed to log in", "password invalid", 401
          )
        except Exception as error:
            print(error)
            return internal_err_resp()