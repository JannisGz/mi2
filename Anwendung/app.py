from flask import Flask, render_template
from fhirclient.client import FHIRClient

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():  # put application's code here
    ecgs = get_ecgs()
    return render_template('baseTemplate.html', title="Example", ecgs=ecgs)


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
