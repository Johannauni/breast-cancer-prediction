from shared import db, app
from patients import Patient
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from functools import wraps
from flask import redirect, url_for

# Login-Wrapper wie in der VL
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if session.get("patient_id") is None:
            return redirect(url_for("login"))
        else:
            return function(*args, **kwargs)
    return wrapper

# Alle Patienten lesen
def get_all_patients():
    with app.app_context():
        return [p.__dict__ for p in Patient.query.all()]

#Patient per id finden
def get_patient_by_id(patient_id):
    with app.app_context():
        patient = Patient.query.filter_by(id=patient_id).first()
        return patient

# Patient per Email lesen
def get_patient_by_email(email):
    with app.app_context():
        return Patient.query.filter_by(email=email).first()

# Patient per ID lesen
def get_all_patients():
    with app.app_context():
        patients = Patient.query.all()
        return [{"id": p.id, "name": p.name, "result": p.result, "user_id": p.user_id} for p in patients]

# Patient hinzufügen
def add_patient(name, email, password):
    with app.app_context():
        patient = Patient(
            name=name,
            email=email,
            password=generate_password_hash(password),
            result=None
        )
        db.session.add(patient)
        db.session.commit()

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
def update_patient_name(name, new_name):
    with app.app_context():
        patient = Patient.query.filter_by(name=name).first()
        if patient:
            patient.name = new_name
            db.session.commit()

# Patient löschen
def delete_patient(name):
    with app.app_context():
        patient = Patient.query.filter_by(name=name).first()
        if patient:
            db.session.delete(patient)
            db.session.commit()
            return True
        return False

# Initialisierung — ersten Admin-Patient anlegen, falls leer
def init():
    with app.app_context():
        if Patient.query.count() == 0:
            patient = Patient(
                name="Admin",
                email="admin@test.de",
                password=generate_password_hash("admin123"),
                result=None
            )
            db.session.add(patient)
            db.session.commit()
            print("Admin-Patient angelegt!")