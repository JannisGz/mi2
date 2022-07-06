from flask import request, flash, redirect, send_file, url_for, jsonify
from flask_restx import Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, get_current_user, get_jwt_identity
from Anwendung.app.database.user import User as dbUser
from Anwendung.app.database.user import Patient as dbPat
from Anwendung.app.database.user import Pratice as dbPra
ns = Namespace('patients', description='operations available when accessing Patient overview')
patient = ns.model('Patient', {
    'id': fields.Integer(readOnly=True, description='The identifier patient'),
    'username': fields.String(required=True, description='Username of the patient'),

})
@ns.route('/patients')
class Patients(Resource):
    @jwt_required()
    @ns.doc('An overview of all available patients')
    def get(self):
        result = []
        user = dbUser.query.filter(dbUser.id==get_jwt_identity()).one()
        username = user.username
