from flask import Flask
from users.controllers.user_controller import user_controller
from db.db import db
from flask_cors import CORS

# 🔥 IMPORTANTE: importar el modelo
from users.models.user_model import Users

app = Flask(__name__)
app.secret_key = 'secret123'
app.config.from_object('config.Config')

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(user_controller)
CORS(app, supports_credentials=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

