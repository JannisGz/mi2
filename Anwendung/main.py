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

url_base = 'http://localhost'
fhir_url = url_base + ':8080/fhir'
web_url = url_base + ':5000'
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
        practises.append((practise.username, practise.id, practise.name))
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
        practises.append((practise.username, practise.id, practise.name))
    return practises


def setClearance(username, practisename):
    """
    Inverts the clearance currently set for pair of (patient:username, practise:username
    """
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
    F??gt eine Freigabe f??r einen Benutzer fest.

    :param user_name: Name des Benutzers dessen Daten freigegeben werden
    :param practices: Praxen/??rzte f??r welche die Daten freigegeben werden
    :return: void
    """
    # Neue Freigaben hinzuf??gen
    clr = Clearance(username=user_name, practisename=practice)
    db.session.add(clr)
    db.session.commit()


def set_clearances(user_name, practices):
    """
    Legt die Freigaben f??r einen Benutzer fest.

    :param user_name: Name des Benutzers dessen Daten freigegeben werden
    :param practices: Praxen/??rzte f??r welche die Daten freigegeben werden
    :return: void
    """
    # Alte Freigaben l??schen
    clearances = db.session.query(Clearance).filter(Clearance.username == user_name)
    clearances.delete(synchronize_session=False)
    # Neue Freigaben hinzuf??gen
    for practice in practices:
        clr = Clearance(username=user_name, practisename=practice)
        db.session.add(clr)
    db.session.commit()


@main.route("/testroute", methods=["GET"])
def testfunc():
    result = setClearance("Patient1", "Musterpraxis")
    return render_template('login.html', title="Login")


@main.route("/patients", methods=["GET"])
@login_required
def patients():
    """
    Gibt die Gruppen-Ansicht aller Patienten zur??ck, f??r die der eingeloggte Benutzer eine Freigabe erhalten hat.
    F??r Patienten ist diese Seite nicht erreichbar, sie werden auf ihre Einzel-Ansicht umgeleitet.
    Nicht eingeloggte Benutzer werden auf die Login-Seite umgeleitet.

    :return: Patienten-Gruppen-Ansicht (??rzte), Einzelansicht (Patienten), Login (nicht eingeloggte Benutzer)
    """
    # Nur ??rzte haben hier Zugriff
    if current_user.practise:
        patient_ids = getPatientsByClearance(current_user.username)

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
    """
    Gibt die Einzelansicht f??r einen Patienten zur??ck. Diese Seite ist nur f??r eingeloggte Benutzer verf??gbar. Nicht
    eingeloggte Benutzer werden auf die Login-Seite geleitet.

    :param patient_id: Id des angefragten Patienten
    :return: Patient-Einzel-Ansicht oder Login falls nicht eingeloggt
    """
    p = fhir_interface.get_patient(patient_id)
    h = fhir_interface.get_height(patient_id)
    w = fhir_interface.get_weight(patient_id)
    e = fhir_interface.get_ecgs_with_diagnosis(patient_id)

    clearances = getPractisesByClearance(current_user.username)

    patient = dbUser.query.filter_by(fhir_id=patient_id).one()

    return render_template('patient.html', title="Patient " + patient_id, user=current_user, patient_id=patient_id,
                           patient=p, height=h, weight=w, ecgs=e, clearances=clearances, patient2=patient)


@main.route("/patients/<patient_id>/edit", methods=["GET"])
@login_required
def patient_update(patient_id):
    """
    Zeigt die ??nderungsseite f??r einen Patienten an. Benutzer muss eingeloggt sein.

    :param patient_id: Id des Patienten
    :return: ??nderungsseite, bzw. Login
    """
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
    """
    Wertet ??nderungsformular f??r einen Benutzer aus. Bei invaliden Angaben wir das Formular erneut angezeigt mit einer
    entsprechenden Fehlermeldung. Bei Erfolg wird die Einzelansicht des Patienten angezeigt.

    :param patient_id:
    :return: Patientenansicht bei Erfolg, sonst ??nderungsansicht
    """
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
    # Alle Felder m??ssen gesetzt sein (au??er Passwort-Neu und Wiederholen)
    if not firstname or not lastname or not email or not phone or not password_old or not email_repeat:
        flash('Alle Felder m??ssen ausgef??llt sein.', 'error')
        return redirect(url_for('main.patient_update', patient_id=patient_id))
    elif email_repeat and email != email_repeat:
        flash('Die gesetzten E-Mail-Adressen m??ssen identisch sein.', 'error')
        return redirect(url_for('main.patient_update', patient_id=patient_id))
    elif (password or password_repeat) and password != password_repeat:
        flash('Die gesetzten Passw??rter m??ssen identisch sein.', 'error')
        return redirect(url_for('main.patient_update', patient_id=patient_id))
    else:
        # Altes Passwort (password_old) ??berpr??fen
        user = dbUser.query.filter_by(username=current_user.username).first()
        if not user or not check_password_hash(user.password, password_old):
            flash('Ung??ltige Zugangsdaten.', 'error')
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
    """
    Detailansicht zu einem EKG f??r einen Patienten.

    :param patient_id: Id des Patienten
    :param ecg_id: Id des EKGs
    :return: EKG-Ansicht, Login-Screen f??r nicht eingeloggte Nutzer
    """
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

    return render_template('ecg.html', title="EKG " + ecg_id + " f??r Patient " + patient_id, user=current_user,
                           ecg=e, patient=p, diagnosis=d, height=h, weight=w, ecg_data=ecg_data,
                           diagnosis_radio=diagnosis_radio)


@main.route("/patients/<patient_id>/ecg/<ecg_id>", methods=["POST"])
@login_required
def patient_ecg_post(patient_id, ecg_id):
    """
    Wertet das ??nderungsformular f??r EKGs aus. Hier kann eine Diagnose zu einem EKG hinzugef??gt oder ge??ndert werden.

    :param patient_id: Id des Patienten
    :param ecg_id: Id des EKGs
    :return: EKG-Seite
    """
    # Nur ??rzte haben hier Zugriff
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
    """
    Zeigt die Hilfeseite an. Hier werden die Anleitung f??r das Erstellen von EKGs und synchronisieren mit Hilfe des
    iPhones angezeigt.
    """
    p = fhir_interface.get_patient(patient_id)
    return render_template('help.html', title="Anleitungen", user=current_user, patient=p, server_url=fhir_url)


@main.route("/patients/new", methods=["GET"])
@login_required
def patient_new():
    # Nur ??rzte haben hier Zugriff
    if current_user.practise:
        return render_template('new_patient.html', title="Neuer Patient", user=current_user)
    return redirect(url_for('main.patients'))


@main.route("/patients/new", methods=["POST"])
@login_required
def patient_new_post():
    """
    Wertet das Formular zur Erstellung eines neuen Patienten aus. Bei ung??ltigen Angaben wird das Formular erneut
    angezeigt. Bei Erfolg wird die Patienten-Gruppen-Ansicht f??r den erstellenden Arzt angezeigt.
    F??r nicht eingeloggte Benutzer und Patienten ist diese Seite nicht erreichbar.

    :return: Patienten-Gruppen-Ansicht (Erfolg), Formular (Misserfolg), Einzel-Ansicht (Patienten),
            Login (Falls nicht eingloggt)
    """
    # Nur ??rzte haben hier Zugriff
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
        # Alle Felder m??ssen gesetzt sein
        if not firstname or not lastname or not username or not email or not email_repeat or not phone or not birthdate:
            flash('Alle Felder m??ssen ausgef??llt sein.', 'error')
            return redirect(url_for('main.patient_new'))
        elif email != email_repeat:
            flash('Die gesetzten E-Mail-Adressen m??ssen identisch sein.', 'error')
            return redirect(url_for('main.patient_new'))
        else:
            user = dbUser.query.filter_by(
                username=username).first()
            if user:
                flash('Der Nutzername existiert bereits.', 'error')
                return redirect(url_for('main.patient_new'))

            fhir_id = fhir_interface.create_patient(firstname, lastname, birthdate, "female", username)

            password = lastname+''.join(random.choice(string.ascii_letters) for i in range(4))
            new_User = dbUser(email=email, name=firstname+" "+lastname, username=username,practise=False, fhir_id=fhir_id, \
                              password=generate_password_hash(password, method='sha256'), telephone=phone)

            db.session.add(new_User)
            add_clearance(username, current_user.username)
            db.session.commit()
            proc = mp.Process(target = Mail.send_mail_created, args = (email, username, password, web_url))
            proc.start()
            flash('Patient hinzugef??gt. Ein Passwort wird per Mail versand, dies kann wenige Minuten dauern.', "success")
            return redirect(url_for('main.patients', title="Patient " + fhir_id, username=current_user.name,
                                    patient_id=fhir_id, patient_name=lastname + ", " + firstname, birth_date=birthdate))
    else:
        return redirect(url_for('main.patients'))
