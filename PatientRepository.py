from shared import db, app
from patients import Patient
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from functools import wraps
from flask import redirect, url_for
from User import User

#Patient per id finden
def get_patient_by_id(patient_id):
    with app.app_context():
        patient = Patient.query.filter_by(id=patient_id).first()
        return patient

# Alle Patienten (angelegt durch User) lesen
def get_all_patients():
    with app.app_context():
        patients = Patient.query.filter(Patient.user_id != None).all()
        return [{"id": p.id, "name": p.name, "result": p.result, "user_id": p.user_id} for p in patients]


def add_patient_with_result(name, user_id, result):
    with app.app_context():
        patient = Patient(
            name=name,
            user_id=user_id,  # wer hat ihn angelegt
            result=result
        )
        db.session.add(patient)
        db.session.commit()

# Ergebnis aktualisieren
def update_patient_result(patient_id, result):
    with app.app_context():
        patient = Patient.query.filter_by(id=patient_id).first()
        if patient:
            patient.result = result
            db.session.commit()

# Namen aktualisieren
def update_patient_name(patient_id, new_name):
    with app.app_context():
        patient = Patient.query.filter_by(id=patient_id).first()
        if patient:
            patient.name = new_name
            db.session.commit()

# Patient löschen
def delete_patient(patient_id):
    with app.app_context():
        patient = Patient.query.filter_by(id=patient_id).first()
        if patient:
            db.session.delete(patient)
            db.session.commit()
