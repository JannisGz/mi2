from flask import Flask, render_template
from fhirclient.client import FHIRClient

app = Flask(__name__)

username = "Max Mustermann"


@app.route("/test", methods=["GET", "POST"])
def index():  # put application's code here
    ecgs = get_ecgs()
    return render_template('base.html', title="Example", ecgs=ecgs)


@app.route("/", methods=["GET", "POST"])
def login():
    return render_template('login.html', title="Login")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    return render_template('login.html', title="Login")


@app.route("/patients", methods=["GET"])
def get_all_patients():
    return render_template('patients.html', title="Patienten", username=username)


@app.route("/patients/<patient_id>", methods=["GET"])
def get_patient(patient_id):
    return render_template('patient.html', title="Patient " + patient_id, username=username, patient_id=patient_id,
                           patient_name="Wolf, Dieter", birth_date="01.03.1947")


@app.route("/patients/<patient_id>/edit", methods=["GET", "POST"])
def edit_patient(patient_id):
    return render_template('edit_patient.html', title="Daten für Patient " + patient_id, username=username,
                           patient_id=patient_id)


@app.route("/patients/<patient_id>/ecg/<ecg_id>", methods=["GET", "POST"])
def patient_ecg(patient_id, ecg_id):
    return render_template('ecg.html', title="EKG " + ecg_id + " für Patient " + patient_id, username=username,
                           patient_id=patient_id, ecg_id=ecg_id,patient_name="Wolf, Dieter", birth_date="01.03.1947", ecg_datetime="01.07.2022")


@app.route("/patients/<patient_id>/help", methods=["GET"])
def get_help(patient_id):
    return render_template('help.html', title="Anleitungen", username=username, patient_id=patient_id)


@app.route("/patients/new", methods=["GET", "POST"])
def create_patient():
    return render_template('new_patient.html', title="Neuer Patient", username=username)


def get_ecgs():
    settings = {
        "app_id": "my_app",
        "api_base": "http://localhost:8080/fhir/"
    }
    client = FHIRClient(settings)
    result = client.server.request_json(path="Observation")
    results = []
    """
    Result ist wie folgt aufgebaut (JSON):
    entry (Liste) -> resource -> ? -> Irgendwann kommt das EKG
    Todo
    """
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0')
