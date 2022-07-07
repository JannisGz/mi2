import json
from fhirpy import SyncFHIRClient
from fhirpy.base.searchset import Raw
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.annotation import Annotation
from fhir.resources.contactpoint import ContactPoint
import random
import time


class FHIRInterface:
    def __init__(self, url):
        self.client = SyncFHIRClient(url=url, extra_headers={"x-api-key":"api-key"})
        self.patients_resources = self.client.resources('Patient')
        self.observation_resources = self.client.resources('Observation')

    def get_height(self, patient_id: str):
        '''
        :param patient_id:
        :return: Observation object of last updated height
        '''
        try:
            patient =  self.patients_resources.search(_id=patient_id).first()
            observation = self.observation_resources.search(subject=patient, code="8302-2").sort("_lastUpdated").fetch_all()[-1]
            return str(observation.valueQuantity["value"]) + " " + str(observation.valueQuantity["unit"])
        except:
            return "keine Messung vorhanden"

    def get_weight(self, patient_id: str):
        '''
        :param patient_id:
        :return: Observation object of last updated weight
        '''
        try:
            patient =  self.patients_resources.search(_id=patient_id).first()
            observation = self.observation_resources.search(subject=patient, code="29463-7").sort("_lastUpdated").fetch_all()[-1]
            return str(observation.valueQuantity["value"]) + " " + str(observation.valueQuantity["unit"])
        except:
            return "keine Messung vorhanden"

    def get_patient(self, patient_id: str):
        '''
        :param patient_id:
        :return: Patient object
        '''
        patient = self.client.reference('Patient', patient_id).to_resource()
        return Patient.parse_obj(patient)

    def get_dob(self, patient_id: str):
        '''
        :param patient_id:
        :return: Birthdate String 'yyyy-mm-dd'
        '''
        patient = self.client.reference('Patient', patient_id).to_resource()
        patient = Patient.parse_obj(patient)
        return patient.birthDate

    def get_gender(self, patient_id: str):
        '''
        :param patient_id:
        :return: Gender String
        '''
        patient = self.client.reference('Patient', patient_id).to_resource()
        patient = Patient.parse_obj(patient)
        return patient.gender

    def get_names(self, patient_id: str):
        '''
        :param patient_id:
        :return: Tuple (family name, given name)
        '''
        patient = self.client.reference('Patient', patient_id).to_resource()
        patient = Patient.parse_obj(patient)
        return patient.name[0].family, patient.name[0].given[0]

    def get_ecgs(self, patient_id: str):
        '''
        :param patient_id:
        :return: List of Observation Objects sorted newest to oldest
        '''
        patient =  self.patients_resources.search(_id=patient_id).first()
        observations = self.observation_resources.search(subject=patient, code="131328").sort("_lastUpdated").fetch_all()
        observations = [Observation.parse_obj(observation) for observation in observations]
        return observations

    def get_observation(self, observation_id: str):
        '''
        :param patient_id:
        :return: Observation Object
        '''
        observation = self.client.reference('Observation', observation_id).to_resource()
        return Observation.parse_obj(observation)

    def get_id(self, name_first: str, name_family: str, rand_identifier: str):
        '''
        helper function for create_patient
        :param name_first:
        :param name_family:
        :param rand_identifier: created with patient in create_patient
        :return: patient id
        '''
        ret = 0
        c = 0
        while (ret == 0):
            time.sleep(0.5)
            patients = self.patients_resources.search(family=name_family, given=name_first).fetch_all()
            for patient in patients:
                if patient.identifier[0].id == rand_identifier:
                    return patient.id
            c += 1
            if c == 600:
                return 0

    def create_patient(self, name_first: str, name_family: str, dob: str, gender: str):
        '''
        :param name_first: String
        :param name_family: String
        :param dob: String
        :param gender: String
        :return: FHIR Patient Reference id
        '''
        patient = Patient()

        rand = random.randint(100, 9999999)
        identifier = Identifier()
        identifier.id = str(rand)
        patient.identifier = [identifier]

        name = HumanName()
        name.use = "official"
        name.family = name_family
        name.given = [name_first]
        patient.name = [name]

        patient.birthDate = dob
        patient.gender = gender

        self.client.resource('Patient', **json.loads(patient.json())).save()

        return self.get_id(name_first, name_family, str(rand))

    def update_patient(self, id: str, name_first_new=None, name_family_new=None, dob_new=None, gender_new=None):
        """
        updates name (first & last), birthdate and gender
        :param id:
        :param name_first_new:
        :param name_family_new:
        :param dob_new:
        :param gender_new:
        :return: -
        """
        patient = self.get_patient(id)
        name = HumanName.parse_obj(patient.name[0])
        if name_family_new != None:
            name.family = name_family_new
        if name_first_new != None:
            name.given = [name_first_new]
        patient.name = [name]

        if dob_new != None:
            patient.birthDate = dob_new
        if gender_new != None:
            patient.gender = gender_new

        self.client.resource('Patient',**json.loads(patient.json())).save()

    def set_diagnosis(self, ecg_id, icd_10_code=None):
        ecg = self.get_observation(ecg_id)
        data = {"text": icd_10_code }
        note = Annotation(**data)
        ecg.note = [note]

        self.client.resource('Observation',**json.loads(ecg.json())).save()

    def get_diagnosis(self, ecg_id):
        ecg = self.get_observation(ecg_id)
        try:
            return ecg.note[0].text
        except:
            return "-"

    def get_ecgs_with_diagnosis(self, patient_id):
        ecgs = self.get_ecgs(patient_id)
        ecg_diagnosis = []
        for ecg in ecgs:
            ecg_diagnosis.append((ecg, self.get_diagnosis(ecg.id)))
        return ecg_diagnosis

    def get_ecgs_new(self, patient_id):
        ecgs = self.get_ecgs(patient_id)
        ecgs_new = []
        for ecg in ecgs:
            try:
                ecg.note[0].text
            except:
                ecgs_new.append(ecg)
        return ecgs_new

    def get_ecg_newest_date(self, patient_id):
        try:
            ecg = self.get_ecgs(patient_id).pop()
            return (ecg.meta.lastUpdated.strftime("%Y-%m-%d %H:%M:%S"))
        except:
            return "-"

'''
interface = FHIRInterface('http://localhost:8080/fhir')
print(interface.create_patient("First", "Last", "2020-01-01", "male"))
print(interface.get_patient("60").json())
print(interface.get_height("60").json())
print(interface.get_weight("60").json())
print(interface.get_names("60"))
print(interface.get_dob("60"))
print(interface.get_gender("60"))
print(interface.get_ecgs("60")[0].json())
print(interface.get_observation("106").json())
interface.update_patient("61", "new_first1", "new_family1", gender_new="female")
interface.set_diagnosis("124", "diagnose")
print(interface.get_diagnosis("124"))
'''
