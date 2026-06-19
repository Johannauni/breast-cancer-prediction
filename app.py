from flask import Flask, json, jsonify, make_response, abort, render_template, session
from flask import request
import pickle
import numpy as np
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect
import jwt


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_super_secret_key_only_known_by_the_server'
with open("model/model.pkl", "rb") as f: #Modell öffnen
    model_data = pickle.load(f)

# Die 4 gespeicherten Werte aus dem Modell holen
w = model_data["w"]
mean_train = model_data["mean_train"]
std_train = model_data["std_train"]
features = model_data["features"] # Liste der Feature-Namen

#Patientenliste + Hilfsfunktionen
patients = []
def pos_by_email(email):
    for pos, obj in enumerate(patients):
        if obj['email'] == email:
            return pos
    return -1

# Hilfsfunktion: Patient per ID finden
def pos_by_id(user_id):
    for pos, obj in enumerate(patients):
        if obj['id'] == user_id:
            return pos
    return -1

# Vorhersage-Funktion — genau wie im Trainings-Skript
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
        pos = pos_by_id(data['user_id'])
        if pos == -1:
            abort(401)
        return patients[pos]
    except Exception as e:
        abort(500)

@app.route("/")
def index():       # Startseite
    return render_template("index.html")

@app.route("/predict", methods=["GET", "POST"])
def predict():
    result = None
    values = {}
    # Nur für eingeloggte Patienten
    if "patient_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        feature_values = []
        for f in features:
            val = float(request.form[f])
            values[f] = val
            feature_values.append(val)
        result = predict_case(feature_values)

        # Ergebnis dem eingeloggten Patienten zuordnen
        patient_id = session.get("patient_id")
        for p in patients:
            if p["id"] == patient_id:
                p["result"] = result

    return render_template("predict.html", result=result, features=features, values=values)

@app.route("/eda")
def eda():
    return render_template("eda.html")

@app.route("/history")
def history_view():
    public_history = [{"id": p["id"], "name": p["name"], "result": p["result"]} for p in patients]
    return render_template("history.html", history=public_history)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Prüfen, ob Email schon existiert
        if pos_by_email(email) != -1:
            return render_template("register.html", error="Email bereits vergeben!")

        patient = {
            "id": len(patients) + 1,
            "name": name,
            "email": email,
            "password": generate_password_hash(password),  # Passwort verschlüsseln
            "result": None  # noch keine Vorhersage
        }
        patients.append(patient)
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        pos = pos_by_email(email)
        if pos == -1:
            return render_template("login.html", error="Email nicht gefunden!")

        patient = patients[pos]
        if not check_password_hash(patient["password"], password):
            return render_template("login.html", error="Falsches Passwort!")

        # JWT Token erstellen
        token = jwt.encode(
            {"user_id": patient["id"]},
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        session["token"] = token
        session["patient_name"] = patient["name"]
        session["patient_id"] = patient["id"]
        return redirect("/predict")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# GET — alle Patienten als JSON abrufen
@app.route("/patients", methods=["GET"])
def all_patients():
    if "patient_id" not in session:
        return redirect("/login")
    return render_template("patients.html", patients=patients)

# GET — einzelnen Patienten abrufen
@app.route("/patients/<name>", methods=["GET"])
def specific_patient(name):
    current_user = decode_token(request)  # Token prüfen
    for p in patients:
        if p["name"] == name:
            return jsonify(p)
    abort(404)

# DELETE — Patienten löschen
@app.route("/patients/<name>", methods=["DELETE"])
def delete_patient(name):
    current_user = decode_token(request)  # Token prüfen
    for i, p in enumerate(patients):
        if p["name"] == name:
            del patients[i]
            return make_response("", 200)
    abort(404)

# PUT — Patienten aktualisieren
@app.route("/patients/<name>", methods=["PUT"])
def update_patient(name):
    current_user = decode_token(request)  # Token prüfen
    for p in patients:
        if p["name"] == name:
            data = request.get_json()
            p["name"] = data.get("name", p["name"])
            return jsonify(p)
    abort(404)

if __name__ == "__main__":
    app.run(debug=True)