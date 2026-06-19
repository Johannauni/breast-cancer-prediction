from flask import Flask, json, jsonify, make_response, abort, render_template
from flask import request
import pickle
import numpy as np
import io
import base64
import matplotlib



app = Flask(__name__)
with open("model/model.pkl", "rb") as f: #Modell öffnen
    model_data = pickle.load(f)

# Die 4 gespeicherten Werte aus dem Modell holen
w = model_data["w"]
mean_train = model_data["mean_train"]
std_train = model_data["std_train"]
features = model_data["features"] # Liste der Feature-Namen

# Vorhersage-Funktion — genau wie in deinem Trainings-Skript
def predict_case(feature_values):
    X = np.array(feature_values)
    X = (X - mean_train) / std_train
    X = np.insert(X, 0, 1)
    pred = np.sign(X @ w)
    return "Gutartig" if pred == 1 else "Bösartig"

history = []  # Leere Liste für den Verlauf

@app.route("/")
def index():       # Startseite
    return render_template("index.html")

# methods=["GET", "POST"]: GET = Seite aufrufen, POST = Formular absenden
@app.route("/predict", methods=["GET", "POST"]) #Brustkrebs Klassifizierung von neuen Patientendaten
def predict():
    result = None #bisher noch keine Ergebnisse
    values = {} # noch keine Eingaben
    if request.method == "POST": # nur wenn Formular abgeschickt wurde
        feature_values = []
        for f in features: #für jedes Feature einen wert erfragen
            val = float(request.form[f]) # Wert aus dem Formular holen
            values[f] = val
            feature_values.append(val)
        result = predict_case(feature_values) # Vorhersage berechnen
        history.append({"features": values, "result": result}) # speichern
    # result, features und values an das Template weitergeben
    return render_template("predict.html", result=result, features=features, values=values)

def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode()

@app.route("/eda")
def eda():
    return render_template("eda.html")

@app.route("/history")
def history_view():
    return render_template("history.html")

if __name__ == "__main__":
    app.run(debug=True)