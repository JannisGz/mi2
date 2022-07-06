from extensions import db

def reset():
    db.drop_all()
    db.create_all()

def add_patient(db_patient):
    db.session.add(db_patient)
    db.session.commit()

def delete_patient(db_patient):
    db.session.remove(db_patient)
    db.session.commit()