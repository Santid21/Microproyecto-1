# 🧩 MICROPROYECTO 1 – Computación en la Nube

**Universidad Autónoma de Occidente**
Autor: Santiago Duque Valencia

---

# 📌 DESCRIPCIÓN GENERAL

Se implementó una arquitectura de microservicios compuesta por:

* micro_users
* micro_products
* micro_orders
* frontend
* 3 bases de datos MySQL independientes
* Consul para descubrimiento de servicios

Se cumple el requerimiento de persistencia desacoplada y comunicación dinámica entre servicios.

---

# 🏗️ PRIMERA PARTE – Microservicio de Órdenes 

## 📁 Estructura

```text
microOrders/
├── config.py
├── db/db.py
├── orders/
│   ├── controllers/order_controller.py
│   ├── models/order_model.py
│   └── views.py
└── run.py
```

---

## 🔹 config.py

```python
import os

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://root:root@mysql_orders/orders_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

## 🔹 db/db.py

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

---

## 🔹 models/order_model.py

```python
from db.db import db

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    user_email = db.Column(db.String(100))
    total = db.Column(db.Float)
```

---

## 🔹 controllers/order_controller.py

```python
from flask import Blueprint, request, jsonify, session
from db.db import db
from orders.models.order_model import Order
import requests

order_controller = Blueprint("order_controller", __name__)

CONSUL_URL = "http://consul:8500/v1/catalog/service/micro_products"

def discover_products_service():
    response = requests.get(CONSUL_URL)
    service = response.json()[0]
    return f"http://{service['ServiceAddress']}:{service['ServicePort']}"

@order_controller.route('/api/orders', methods=['GET'])
def get_all_orders():
    orders = Order.query.all()
    return jsonify([{
        "id": o.id,
        "user_name": o.user_name,
        "user_email": o.user_email,
        "total": o.total
    } for o in orders])

@order_controller.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"message": "Orden no encontrada"}), 404
    return jsonify({
        "id": order.id,
        "user_name": order.user_name,
        "user_email": order.user_email,
        "total": order.total
    })

@order_controller.route('/api/orders', methods=['POST'])
def create_order():

    data = request.get_json()
    user_name = session.get('username')
    user_email = session.get('email')

    if not user_name or not user_email:
        return jsonify({"message": "Información de usuario inválida"}), 400

    products = data.get("products")
    if not products:
        return jsonify({"message": "Productos inválidos"}), 400

    products_service_url = discover_products_service()
    total = 0

    for item in products:
        product_id = item["id"]
        quantity = item["quantity"]

        product_response = requests.get(f"{products_service_url}/api/products/{product_id}")

        if product_response.status_code == 404:
            return jsonify({"message": "Producto no existe"}), 404

        product = product_response.json()

        if product["stock"] < quantity:
            return jsonify({"message": "Inventario insuficiente"}), 409

        total += product["price"] * quantity

        requests.put(
            f"{products_service_url}/api/products/{product_id}",
            json={"stock": product["stock"] - quantity}
        )

    new_order = Order(
        user_name=user_name,
        user_email=user_email,
        total=total
    )

    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": "Orden creada exitosamente"}), 201
```

---

## 🔹 run.py

```python
from flask import Flask
from config import Config
from db.db import db
from orders.views import order_controller
import requests
import socket

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
app.register_blueprint(order_controller)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

def register_service():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    service_data = {
        "Name": "micro_orders",
        "Address": ip,
        "Port": 5000,
        "Check": {
            "HTTP": f"http://{ip}:5000/health",
            "Interval": "10s"
        }
    }

    requests.put("http://consul:8500/v1/agent/service/register", json=service_data)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    register_service()
    app.run(host="0.0.0.0", port=5000)
```

---

# 🐳 SEGUNDA PARTE – Docker y Compose 

## 🔹 Dockerfile (para cada microservicio)

```dockerfile
FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install flask flask_sqlalchemy mysqlclient pymysql flask-cors requests

EXPOSE 5000

CMD ["python", "run.py"]
```

---

## 🔹 docker-compose.yml

```yaml
version: "3.8"

services:

  consul:
    image: hashicorp/consul:1.15
    ports:
      - "8500:8500"

  mysql_users:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: users_db

  mysql_products:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: products_db

  mysql_orders:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: orders_db

  micro_users:
    build: ./microUsers
    depends_on:
      - mysql_users
      - consul

  micro_products:
    build: ./microProducts
    depends_on:
      - mysql_products
      - consul

  micro_orders:
    build: ./microOrders
    depends_on:
      - mysql_orders
      - consul

  frontend:
    build: ./frontend
    ports:
      - "8000:5001"
    depends_on:
      - micro_users
      - micro_products
      - micro_orders
```

---

# 🧭 TERCERA PARTE – Descubrimiento con Consul 

Se implementa:

✔ Registro automático vía API
✔ Health Check
✔ Descubrimiento dinámico

Endpoint Consul usado:

```python
http://consul:8500/v1/catalog/service/micro_products
```

No existe URL hardcodeada del servicio de productos.

---

# 🚀 Ejecución

```bash
docker compose build --no-cache
docker compose up -d
docker ps
```

---

# 🎯 Conclusión

El sistema implementa una arquitectura desacoplada, escalable y alineada con principios de computación en la nube, cumpliendo todos los requerimientos del microproyecto.
