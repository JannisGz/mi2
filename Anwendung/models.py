from flask_login import UserMixin
from . import db
from datetime import datetime


Column = db.Column
Model = db.Model
relationship = db.relationship



class User(UserMixin, Model):
    """ User model for storing user related data """
    __tablename__ = 'user'
    id = Column(db.Integer, primary_key=True)
    email = Column(db.String(64))
    name = Column(db.String(64), nullable=True)
    username = Column(db.String(15), unique=True, index=True)
    password = Column(db.String(128))
    practise = Column(db.Boolean, default=False)
    fhir_id = Column(db.Integer, nullable=True)



class Clearance(Model):
    __tablename__ = 'clearances'
    id = Column(db.Integer, primary_key=True)
    username = Column(db.String(15), db.ForeignKey('user.username'))
    practisename = Column(db.String(15), db.ForeignKey('user.username'))



