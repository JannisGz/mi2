from flask_jwt_extended import create_access_token
from Anwendung.app.database.models import UserSchema
from Anwendung.app.database.user import User
from datetime import datetime
from Anwendung.app.extensions import db
from flask import current_app
user_schema = UserSchema()

def message(status, message):
    response_object ={"status":status, "message":message}
    return response_object


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
        # Assign vars
        username = data["username"]
        password = data["password"]

        try:
            # Fetch user data
            if not (user := User.query.filter_by(username=username).first()):
                return err_resp(
                    "The email you have entered does not match any account.",
                    "email_404",
                    404,
                )

            elif user and user.verify_password(password):
                user_info = user_schema.dump(user)

                access_token = create_access_token(identity=user.id)

                resp = message(True, "Successfully logged in.")
                resp["access_token"] = access_token
                resp["user"] = user_info

                return resp, 200

            return err_resp(
                "Failed to log in, password may be incorrect.", "password_invalid", 401
            )

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def register(data):
        # Assign vars

        ## Required values
        email = data["email"]
        username = data["username"]
        password = data["password"]

        ## Optional
        data_name = data.get("name")

        # Check if the email is taken
        if User.query.filter_by(email=email).first() is not None:
            return err_resp("Email is already being used.", "email_taken", 403)

        # Check if the username is taken
        if User.query.filter_by(username=username).first() is not None:
            return err_resp("Username is already taken.", "username_taken", 403)

        try:
            new_user = User(
                email=email,
                username=username,
                name=data_name,
                password=password,
                joined_date=datetime.utcnow(),
            )

            db.session.add(new_user)
            db.session.flush()

            # Load the new user's info
            user_info = user_schema.dump(new_user)

            # Commit changes to DB
            db.session.commit()

            # Create an access token
            access_token = create_access_token(identity=new_user.id)
            resp = message(True, "User has been registered.")
            resp["access_token"] = access_token
            resp["user"] = user_info

            return resp, 201

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()