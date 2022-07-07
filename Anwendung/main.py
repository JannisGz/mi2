from flask import Blueprint, Flask, render_template, flash
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


username = "Max Mustermann"


@main.route("/patients", methods=["GET"])
@login_required
def patients():
    return render_template('patients.html', title="Patienten", username=current_user.name)


@main.route("/patients/<patient_id>", methods=["GET"])
@login_required
def patient(patient_id):
    return render_template('patient.html', title="Patient " + patient_id, username=current_user.name, patient_id=patient_id,
                           patient_name="Wolf, Dieter", birth_date="01.03.1947")


@main.route("/patients/<patient_id>/edit", methods=["GET", "POST"])
@login_required
def patient_update(patient_id):
    return render_template('edit_patient.html', title="Daten für Patient " + patient_id, username=current_user.name,
                           patient_id=patient_id)


@main.route("/patients/<patient_id>/ecg/<ecg_id>", methods=["GET", "POST"])
@login_required
def patient_ecg(patient_id, ecg_id):
    return render_template('ecg.html', title="EKG " + ecg_id + " für Patient " + patient_id, username=current_user.name,
                           patient_id=patient_id, ecg_id=ecg_id, patient_name="Wolf, Dieter", birth_date="01.03.1947", ecg_datetime="01.07.2022")


@main.route("/patients/<patient_id>/help", methods=["GET"])
@login_required
def help_get(patient_id):
    return render_template('help.html', title="Anleitungen", username=current_user.name, patient_id=patient_id)


@main.route("/patients/new", methods=["GET", "POST"])
@login_required
def patient_post():
    return render_template('new_patient.html', title="Neuer Patient", username=current_user.name)
