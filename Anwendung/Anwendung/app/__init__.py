from flask import Flask, redirect, render_template, jsonify, request, Blueprint
from flask_restx import Api
import Anwendung.settings as settings
import smtplib
import datetime
from Anwendung.app.auth.auth import auth_ns
from Anwendung.app.extensions import db, bcrypt, jwt, ma, cors


authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
}
api = Api(version='0.1', title='Backend API', security='Bearer Auth', authorizations=authorizations, description='Backend API for sticker generation')

def configure_app(app):
    app.secret_key = '123'
    app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_EXPANSION
    app.config['RESTX_VALIDATE'] = settings.RESTPLUS_VAL
    app.config['RESTX_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODS'] = settings.SQLALCHEMY_TRACK_MODS

def register_extensions(app):
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    cors.init_app(app)

def init_app(app):
    configure_app(app)
    api_blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.add_namespace(auth_ns)
    api.init_app(api_blueprint)
    app.register_blueprint(api_blueprint)
    register_extensions(app)


username = "Max Mustermann"

gmail_user = "pulseappserver@gmail.com"
gmail_pwd = "qzkigrfvlolpqwuz"
def send_mail():
    address = 'mostermann96@web.de'
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_pwd)
    except Exception as e:
        print(e)

    subject  =  'Änderung in Ihren Diagnosen vom '+ str(datetime.date.today())
    body = 'Ihr Arzt hat soeben eine Diagnose zu Ihrem EKG hinzugefuegt. \n' \
           'Sie koennen diese unter http:0.0.0.0:8080 einsehen'
    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (gmail_user, ", ".join(address), subject, body)
    email_text = email_text.encode("UTF-8")
    try:
        server.sendmail(gmail_user, address, email_text)
        server.close()
        print("success")
        resp = jsonify(success=True)
        return resp
    except Exception as e:
        print(e)
        resp  = jsonify(success=True)
        return resp

def create_app():
    app = Flask(__name__)
    import Anwendung.app.database.models
    import Anwendung.app.database.user
    @app.before_first_request
    def create_tables():
        db.drop_all()
        db.create_all()
        db.session.commit()
    configure_app(app)
    init_app(app)

    @app.route('/')
    def home():
        return redirect('/api')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host= '0.0.0.0')