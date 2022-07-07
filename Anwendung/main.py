from flask import Blueprint, Flask, render_template, flash, url_for, redirect, request
from flask_login import login_required, current_user

from Anwendung.fhir_interface import FHIRInterface

main = Blueprint('main', __name__)

fhir_url = 'http://localhost:8080/fhir'
fhir_interface = FHIRInterface(fhir_url)

username = "Max Mustermann"


@main.route("/patients", methods=["GET"])
@login_required
def patients():
    # Nur Ärzte haben hier Zugriff
    if current_user.practise:
        return render_template('patients.html', title="Patienten", username=current_user.name)
    # Patienten werden auf ihre Patientenseite umgeleitet
    else:
        return redirect(url_for('main.patient', title="Patient" + str(current_user.fhir_id), username=current_user.name,
                                patient_id=current_user.fhir_id))


@main.route("/patients/<patient_id>", methods=["GET"])
@login_required
def patient(patient_id):
    p = fhir_interface.get_patient(patient_id)
    h = fhir_interface.get_height(patient_id)
    w = fhir_interface.get_weight(patient_id)
    e = fhir_interface.get_ecgs_with_diagnosis(patient_id)

    return render_template('patient.html', title="Patient " + patient_id, username=current_user.name, patient_id=patient_id,
                           patient=p, height=h, weight=w, ecgs=e)

@main.route("/patients/<patient_id>/edit", methods=["GET", "POST"])
@login_required
def patient_update(patient_id):
    return render_template('edit_patient.html', title="Daten für Patient " + patient_id, username=current_user.name,
                           patient_id=patient_id)


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

    return render_template('ecg.html', title="EKG " + ecg_id + " für Patient " + patient_id, username=current_user.name,
                           ecg=e, patient=p, diagnosis = d, height=h, weight=w, ecg_data=ecg_data)

@main.route("/patients/<patient_id>/ecg/<ecg_id>", methods=["POST"])
@login_required
def patient_ecg_post(patient_id, ecg_id):
    if request.form.get('diagnosis') == "OB":
        fhir_interface.set_diagnosis(ecg_id, "Ohne Befund")
    else:
        fhir_interface.set_diagnosis(ecg_id, request.form.get('icd_code_text'))

    return redirect(url_for('main.patient', patient_id=patient_id))


@main.route("/patients/<patient_id>/help", methods=["GET"])
@login_required
def help_get(patient_id):
    return render_template('help.html', title="Anleitungen", username=current_user.name, patient_id=patient_id)


@main.route("/patients/new", methods=["GET"])
@login_required
def patient_new():
    return render_template('new_patient.html', title="Neuer Patient", username=current_user.name)


@main.route("/patients/new", methods=["POST"])
@login_required
def patient_new_post():
    # Get form data
    firstname = request.form.get('first_name')
    lastname = request.form.get('last_name')
    username = request.form.get('username')
    email = request.form.get('email')
    email_repeat = request.form.get('email_repeat')
    phone = request.form.get('phone')
    birthdate = request.form.get('birth_date')

    # Validate
    print(firstname)
    print(lastname)
    print(username)
    print(email)
    print(email_repeat)
    print(phone)
    print(birthdate)
    # Alle Felder müssen gesetzt sein
    if not firstname or not lastname or not username or not email or not email_repeat or not phone or not birthdate:
        flash('Alle Felder müssen ausgefüllt sein.', 'error')
        return render_template('new_patient.html', title="Neuer Patient", username=current_user.name)
    elif email != email_repeat:
        flash('Die gesetzten E-Mail-Adressen müssen identisch sein.', 'error')
        return render_template('new_patient.html', title="Neuer Patient", username=current_user.name)
    else:
        # Todo: DB Check if already exist
        # Todo: in DB hinzufügen
        patient_id = "12345"
        # Todo: Als FHIR-Ressource hinzufügen
        flash('Patient erfolgreich hinzugefügt', "success")
        return redirect(url_for('main.patients', title="Patient " + patient_id, username=current_user.name,
                                patient_id=patient_id, patient_name=lastname + ", " + firstname, birth_date=birthdate))


def is_none_or_empty(string) -> bool:
    return not string
