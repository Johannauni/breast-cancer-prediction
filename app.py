import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import app, db
import PatientRepository as repo
import BreastcancerRoutes

def create_app():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///patients.db"
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app

if __name__ == "__main__":
    create_app()
    repo.init()
    app.run(debug=True)