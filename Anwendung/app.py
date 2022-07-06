from flask import Flask, render_template, jsonify
from fhirclient.client import FHIRClient
import smtplib
import datetime
app = Flask(__name__)

username = "Max Mustermann"

gmail_user = "pulseappserver@gmail.com"
gmail_pwd = "qzkigrfvlolpqwuz"


@app.route("/test", methods=["GET", "POST"])
def index():  # put application's code here
    ecgs = get_ecgs()
    return render_template('base.html', title="Example", ecgs=ecgs)


@app.route("/", methods=["GET", "POST"])
def login():
    send_mail()
    return render_template('login.html', title="Login")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    return render_template('login.html', title="Login")


@app.route("/patients", methods=["GET"])
def get_all_patients():
    return render_template('patients.html', title="Patienten", username=username)


@app.route("/patients/<patient_id>", methods=["GET"])
def get_patient(patient_id):
    return render_template('patient.html', title="Patient " + patient_id, username=username)


@app.route("/patients/<patient_id>/edit", methods=["GET", "POST"])
def edit_patient(patient_id):
    return render_template('edit_patient.html', title="Daten für Patient " + patient_id, username=username)


@app.route("/patients/<patient_id>/ecg/<ecg_id>", methods=["GET", "POST"])
def patient_ecg(patient_id, ecg_id):
    return render_template('ecg.html', title="EKG " + ecg_id + " für Patient " + patient_id, username=username)


@app.route("/patients/<patient_id>/help", methods=["GET"])
def get_help(patient_id):
    return render_template('help.html', title="Anleitungen", username=username)


@app.route("/patients/new", methods=["GET", "POST"])
def create_patient():
    return render_template('new_patient.html', title="Neuer Patient")


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

@app.route("/mail", methods= ["GET"])
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


if __name__ == '__main__':
    app.run(host='0.0.0.0')
