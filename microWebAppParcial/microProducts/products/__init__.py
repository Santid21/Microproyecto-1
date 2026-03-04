from flask import Flask
from config import Config
from db.db import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    @app.route("/")
    def home():
        return {"message": "MicroProducts funcionando"}

    return app
