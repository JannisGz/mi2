from datetime import datetime
from extensions import db, bcrypt

Column = db.Column
Model = db.Model
relationship = db.relationship



class User(Model):
    """ User model for storing user related data """
    __tablename__ = 'user'
    id = Column(db.Integer, primary_key=True)
    email = Column(db.String(64))
    username = Column(db.String(15), unique=True, index=True)
    password_hash = Column(db.String(128))
    practise = Column(db.Boolean, default=False)

    joined_date = Column(db.DateTime, default=datetime.utcnow)
    #role_id = Column(db.Integer, db.ForeignKey("roles.id"))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

class Patient(Model):
    __tablename__ = 'patient'
    id = Column(db.Integer, primary_key=True)
    username = Column(db.Strin(15), db.ForeignKey('user.username'))
    fhir_id = Column(db.Integer)
    practicioners = Column(db.VARCHAR(255))
    phone = Column(db.VARCHAR(255))
    weight = Column(db.Integer, nullable=True)
    size = Column(db.Integer, nullable=True)
    dob= Column(db.DateTime, nullable=True)
    lastname = Column(db.String(30))
    firstname = Column(db.String(30))

class Pratice(Model):
    __tablename__ = 'practise'
    id = Column(db.Integer, primary_key=True)
    username = Column(db.Strin(15), db.ForeignKey('user.username'))