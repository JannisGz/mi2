from flask import Blueprint, Flask, render_template, flash, url_for, redirect, request
from flask_login import login_required, current_user
from .extensions import db
from .models import User as dbUser
from .models import Clearance
import random, string
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from .mail import Mail
from .fhir_interface import FHIRInterface
import multiprocessing as mp

main = Blueprint('main', __name__)

fhir_url = 'http://localhost:8080/fhir'
fhir_interface = FHIRInterface(fhir_url)

username = "Max Mustermann"


def getAllPractises():
    """
    Query database for all available practises
    :return: List of Tuples (string: practisename, int: practiseID)
    """
    practises = list()
    query = dbUser.query.filter_by(practise=True)
    for practise in query:
        practises.append((practise.name, practise.id))
    return practises


def getPatientsByClearance(practisename):
    """
    Get patients that made their records available for the currently signed in practise
    :param practisename: automtically taken from path
    :return: List of patients' FHIR_IDs
    """
    patients = list()
    query = Clearance.query.filter_by(practisename=practisename) \
        .join(dbUser, dbUser.username == Clearance.practisename)
    for row in query:
        patients.append((dbUser.query.filter_by(username=row.username).first()).fhir_id)
    return patients


def getPractisesByClearance(username):
    """
    Returns a List of Practises the currently logged in patient has made their records available to
    :param username:
    :return: List of tuples (string: practisename, int: practiseID)
    """
    practises = list()
    query = Clearance.query.filter_by(username=username) \
        .join(dbUser, dbUser.username == Clearance.practisename)
    for row in query:
        practise = dbUser.query.filter_by(username=row.practisename).one()
        practises.append((practise.name, practise.id))
    return practises


def setClearance(username, practisename):
    try:
        query = Clearance.query.filter_by(username=username, practisename=practisename).one()
        db.session.delete(query)
    except:
        clr = Clearance(username=username, practisename=practisename)
        db.session.add(clr)
    db.session.commit()
    Clearance.query.filter_by().one()
    return


def add_clearance(user_name, practice):
    """
    Fügt eine Freigabe für einen Benutzer fest.

    :param user_name: Name des Benutzers dessen Daten freigegeben werden
    :param practices: Praxen/Ärzte für welche die Daten freigegeben werden
    :return: void
    """
    # Neue Freigaben hinzufügen
    clr = Clearance(username=user_name, practisename=practice)
    db.session.add(clr)
    db.session.commit()


def set_clearances(user_name, practices):
    """
    Legt die Freigaben für einen Benutzer fest.

    :param user_name: Name des Benutzers dessen Daten freigegeben werden
    :param practices: Praxen/Ärzte für welche die Daten freigegeben werden
    :return: void
    """
    # Alte Freigaben löschen
    clearances = db.session.query(Clearance).filter(Clearance.username == user_name)
    clearances.delete(synchronize_session=False)
    # Neue Freigaben hinzufügen
    for practice in practices:
        clr = Clearance(username=user_name, practisename=practice)
        db.session.add(clr)
    db.session.commit()


@main.route("/testroute", methods=["GET"])
def testfunc():
    result = setClearance("Patient1", "Musterpraxis")
    print(result)
    return render_template('login.html', title="Login")


@main.route("/patients", methods=["GET"])
@login_required
def patients():
    # Nur Ärzte haben hier Zugriff
    if current_user.practise:
        patient_ids = getPatientsByClearance(current_user.name)

        while None in patient_ids:
            patient_ids.remove(None)
        patients = [(fhir_interface.get_patient(id), len(fhir_interface.get_ecgs_new(id)),
                     fhir_interface.get_ecg_newest_date(id)) for id in patient_ids]

        return render_template('patients.html', title="Patienten", user=current_user, patients=patients)
    # Patienten werden auf ihre Patientenseite umgeleitet
    else:
        return redirect(url_for('main.patient', title="Patient" + str(current_user.fhir_id), user=current_user,
                                patient_id=current_user.fhir_id))


@main.route("/patients/<patient_id>", methods=["GET"])
@login_required
def patient(patient_id):
    p = fhir_interface.get_patient(patient_id)
    h = fhir_interface.get_height(patient_id)
    w = fhir_interface.get_weight(patient_id)
    e = fhir_interface.get_ecgs_with_diagnosis(patient_id)

    clearances = getPractisesByClearance(current_user.username)

    return render_template('patient.html', title="Patient " + patient_id, user=current_user, patient_id=patient_id,
                           patient=p, height=h, weight=w, ecgs=e, clearances=clearances)


@main.route("/patients/<patient_id>/edit", methods=["GET"])
@login_required
def patient_update(patient_id):
    # Nur Patienten haben hier Zugriff
    if current_user.practise:
        return redirect(url_for('main.patients'))
    edited_patient = fhir_interface.get_patient(patient_id)
    all_practices = getAllPractises()
    clearances = getPractisesByClearance(current_user.username)
    return render_template('edit_patient.html', title="Patient bearbeiten " + patient_id, user=current_user,
                           patient=edited_patient, current_user=current_user, practices=all_practices,
                           clearances=clearances)


@main.route("/patients/<patient_id>/edit", methods=["POST"])
@login_required
def patient_update_post(patient_id):
    # Get form data
    patient = fhir_interface.get_patient(patient_id)
    firstname = request.form.get('first_name')
    lastname = request.form.get('last_name')
    email = request.form.get('email')
    email_repeat = request.form.get('email_repeat')
    phone = request.form.get('phone')
    password = request.form.get('password')
    password_old = request.form.get('password_old')
    password_repeat = request.form.get('password_repeat')
    clearances = request.form.getlist('clearance')

    # Validate
    # Alle Felder müssen gesetzt sein (außer Passwort-Neu und Wiederholen)
    if not firstname or not lastname or not email or not phone or not password_old or not email_repeat:
        flash('Alle Felder müssen ausgefüllt sein.', 'error')
        return redirect(url_for('main.patient_update', patient_id=patient_id))
    elif email_repeat and email != email_repeat:
        flash('Die gesetzten E-Mail-Adressen müssen identisch sein.', 'error')
        return redirect(url_for('main.patient_update', patient_id=patient_id))
    elif (password or password_repeat) and password != password_repeat:
        flash('Die gesetzten Passwörter müssen identisch sein.', 'error')
        return redirect(url_for('main.patient_update', patient_id=patient_id))
    else:
        # Altes Passwort (password_old) überprüfen
        user = dbUser.query.filter_by(username=current_user.name).first()

        if not user or not check_password_hash(user.password, password_old):
            flash('Ungültige Zugangsdaten.', 'error')
            return redirect(url_for('main.patient_update', patient_id=patient_id))

        # FHIR Patient aktualisieren
        fhir_interface.update_patient(patient_id, firstname, lastname)
        # Passwort und E-Mail in eigener DB aktualisieren
        user.email = email
        user.telephone = phone
        user.name = firstname + " " + lastname
        if password:
            user.password = generate_password_hash(password, method='sha256')

        db.session.commit()

        # Freigaben aktualisieren
        set_clearances(current_user.username, clearances)

        flash('Patient erfolgreich aktualisiert.', "success")
        return redirect(url_for('main.patient', patient_id=patient_id))


@main.route("/patients/<patient_id>/ecg/<ecg_id>", methods=["GET"])
@login_required
def patient_ecg(patient_id, ecg_id):
    p = fhir_interface.get_patient(patient_id)
    e = fhir_interface.get_observation(ecg_id)
    d = fhir_interface.get_diagnosis(ecg_id)
    h = fhir_interface.get_height(patient_id)
    w = fhir_interface.get_weight(patient_id)
    ecg_data = e.component[0].valueSampledData.data.split(" ")[:-1]
    ecg_data = [float(x) for x in ecg_data]

    # Konvertiere Diagnose in Radiobutton (0 = Keine Diagnose, 1 = ohne Befund, 2 = ICD-Code vorhanden)
    if d is None or d == "-" or d == "":
        diagnosis_radio = 0
    elif d == "ohne Befund":
        diagnosis_radio = 1
    else:
        diagnosis_radio = 2

    return render_template('ecg.html', title="EKG " + ecg_id + " für Patient " + patient_id, user=current_user,
                           ecg=e, patient=p, diagnosis=d, height=h, weight=w, ecg_data=ecg_data,
                           diagnosis_radio=diagnosis_radio)


@main.route("/patients/<patient_id>/ecg/<ecg_id>", methods=["POST"])
@login_required
def patient_ecg_post(patient_id, ecg_id):
    # Nur Ärzte haben hier Zugriff
    if current_user.practise:
        if request.form.get('diagnosis') == "OB":
            fhir_interface.set_diagnosis(ecg_id, "Ohne Befund")
        else:
            fhir_interface.set_diagnosis(ecg_id, request.form.get('icd_code_text'))

        flash('Auswertung gespeichert.', "success")
        return redirect(url_for('main.patient_ecg', patient_id=patient_id, ecg_id=ecg_id))

    return redirect(url_for('main.patient', patient_id=patient_id))


@main.route("/patients/<patient_id>/help", methods=["GET"])
@login_required
def help_get(patient_id):
    p = fhir_interface.get_patient(patient_id)
    return render_template('help.html', title="Anleitungen", user=current_user, patient=p, server_url=fhir_url)


@main.route("/patients/new", methods=["GET"])
@login_required
def patient_new():
    # Nur Ärzte haben hier Zugriff
    if current_user.practise:
        return render_template('new_patient.html', title="Neuer Patient", user=current_user)
    return redirect(url_for('main.patients'))


@main.route("/patients/new", methods=["POST"])
@login_required
def patient_new_post():
    # Nur Ärzte haben hier Zugriff
    if current_user.practise:
        # Get form data
        firstname = request.form.get('first_name')
        lastname = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        email_repeat = request.form.get('email_repeat')
        phone = request.form.get('phone')
        birthdate = request.form.get('birth_date')

        # Validate
        # Alle Felder müssen gesetzt sein
        if not firstname or not lastname or not username or not email or not email_repeat or not phone or not birthdate:
            flash('Alle Felder müssen ausgefüllt sein.', 'error')
            return redirect(url_for('main.patient_new'))
        elif email != email_repeat:
            flash('Die gesetzten E-Mail-Adressen müssen identisch sein.', 'error')
            return redirect(url_for('main.patient_new'))
        else:
            user = dbUser.query.filter_by(
                username=username).first()
            if user:
                flash('Der Nutzername existiert bereits.', 'error')
                return redirect(url_for('main.patient_new'))

            fhir_id = fhir_interface.create_patient(firstname, lastname, birthdate, "female", username)
            print(fhir_id)

            password = lastname+''.join(random.choice(string.ascii_letters) for i in range(4))
            new_User = dbUser(email=email, name=firstname+" "+lastname, username=username,practise=False, fhir_id=fhir_id, \
                              password=generate_password_hash(password, method='sha256'), telephone=phone)

            db.session.add(new_User)
            add_clearance(username, current_user.name)
            db.session.commit()
            proc = mp.Process(target = Mail.send_mail_created, args = (email, username, password))
            proc.start()
            flash('Patient erfolgreich hinzugefügt', "success")
            return redirect(url_for('main.patients', title="Patient " + fhir_id, username=current_user.name,
                                    patient_id=fhir_id, patient_name=lastname + ", " + firstname, birth_date=birthdate))
    else:
        return redirect(url_for('main.patients'))


def is_none_or_empty(string) -> bool:
    return not string
