from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_super_secret_key_only_known_by_the_server'

db = SQLAlchemy()
