from shared import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from functools import wraps
from flask import redirect, url_for
from User import User

# Login-Wrapper wie in der VL
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        else:
            return function(*args, **kwargs)
    return wrapper

# User hinzufügen
def add_user(name, email, password):
    with app.app_context():
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()

# Alle User lesen
def get_all_users():
    with app.app_context():
        users = User.query.filter(User.email != None).all()
        return [{"id": u.id, "name": u.name, "email": u.email} for u in users]

def get_user_by_id(user_id):
    with app.app_context():
        return User.query.filter_by(id=user_id).first()

# User per Email lesen
def get_user_by_email(email):
    with app.app_context():
        return User.query.filter_by(email=email).first()

# Initialisierung — ersten Admin-Patient anlegen, falls leer
def init():
    with app.app_context():
        if User.query.count() == 0:
            user = User(
                name="Admin",
                email="admin@test.de",
                password=generate_password_hash("admin123"),
            )
            db.session.add(user)
            db.session.commit()
            print("Admin-User angelegt!")