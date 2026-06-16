from flask import Flask, json, jsonify, make_response, abort, render_template
from flask import request

app = Flask(__name__)

@app.route("/")
def index():       # Startseite
    return render_template("index.html")

@app.route("/predict", methods=["GET", "POST"]) #Brustkrebs Klassifizierung von neuen Patientendaten
def predict():
    return render_template("predict.html")

@app.route("/eda")
def eda():
    return render_template("eda.html")

@app.route("/history")
def history_view():
    return render_template("history.html")

if __name__ == "__main__":
    app.run(debug=True)