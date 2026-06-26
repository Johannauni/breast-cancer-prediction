import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import render_template, request, redirect, session, jsonify, make_response, abort, url_for, g
from shared import app, db
import PatientRepository as repo
import jwt
import pickle
import numpy as np

# Modell laden
with app.app_context():
    with open("model/model.pkl", "rb") as f:
        model_data = pickle.load(f)

w = model_data["w"]
mean_train = model_data["mean_train"]
std_train = model_data["std_train"]
features = model_data["features"]

# Vorhersage-Funktion
def predict_case(feature_values):
    X = np.array(feature_values)
    X = (X - mean_train) / std_train
    X = np.insert(X, 0, 1)
    pred = np.sign(X @ w)
    return "Gutartig" if pred == 1 else "Bösartig"

# Token dekodieren
def decode_token(request):
    if "Authorization" not in request.headers:
        abort(401)
    token = request.headers["Authorization"]
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        patient = repo.get_patient_by_id(data['user_id'])
        if not patient:
            abort(401)
        return patient
    except Exception:
        abort(500)

# Nutzerobjekt vor jedem Request laden
@app.before_request
def load_user():
    if session.get("patient_id") is not None:
        g.user = repo.get_patient_by_id(session.get("patient_id"))
    else:
        g.user = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["GET", "POST"])
@repo.login_required
def predict():
    result = None
    values = {}
    patient_name = None

    if request.method == "POST":
        # Patientenname aus dem Formular holen
        patient_name = request.form.get("patient_name")

        feature_values = []
        for f in features:
            val = float(request.form[f])
            values[f] = val
            feature_values.append(val)

        # Vorhersage berechnen
        result = predict_case(feature_values)

        # Neuen Patienten mit Ergebnis speichern
        repo.add_patient_with_result(
            name=patient_name,
            user_id=session["patient_id"],
            result=result
        )

    return render_template("predict.html", result=result, features=features, values=values)

@app.route("/eda")
def eda():
    return render_template("eda.html")

@app.route("/history")
def history_view():
    all_patients = repo.get_all_patients()
    # Nur die eigenen Patienten anzeigen
    my_patients = [p for p in all_patients if p["user_id"] == session.get("patient_id")]
    return render_template("history.html", history=my_patients)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        if repo.get_patient_by_email(email):
            return render_template("register.html", error="Email bereits vergeben!")
        repo.add_patient(name, email, password)
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        patient = repo.get_patient_by_email(email)
        if not patient:
            return render_template("login.html", error="Email nicht gefunden!")
        from werkzeug.security import check_password_hash
        if not check_password_hash(patient.password, password):
            return render_template("login.html", error="Falsches Passwort!")
        token = jwt.encode({"user_id": patient.id}, app.config["SECRET_KEY"], algorithm="HS256")
        session["token"] = token
        session["patient_name"] = patient.name
        session["patient_id"] = patient.id
        return redirect("/predict")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/patients", methods=["GET"])
@repo.login_required
def all_patients():
    patients = repo.get_all_patients()
    return render_template("patients.html", patients=patients)

@app.route("/patients/<name>", methods=["GET"])
def specific_patient(name):
    decode_token(request)
    patient = repo.get_patient_by_email(name)
    if not patient:
        abort(404)
    return jsonify({"id": patient.id, "name": patient.name, "email": patient.email, "result": patient.result})

@app.route("/patients/<name>", methods=["DELETE"])
def delete_patient(name):
    decode_token(request)
    repo.delete_patient(name)
    return make_response("", 200)

@app.route("/patients/<name>", methods=["PUT"])
def update_patient(name):
    decode_token(request)
    data = request.get_json()
    new_name = data.get("name", name)
    repo.update_patient_name(name, new_name)
    return jsonify({"name": new_name})