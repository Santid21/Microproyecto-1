from flask import Flask, jsonify
import requests
import socket

app = Flask(__name__)

# ==========================
# HEALTH CHECK
# ==========================
@app.route("/health")
def health():
    return {"status": "healthy"}


# ==========================
# ENDPOINTS
# ==========================
@app.route("/")
def home():
    return {"message": "MicroProducts funcionando"}


@app.route("/api/products")
def get_products():
    products = [
        {"id": 1, "name": "Laptop", "price": 2500},
        {"id": 2, "name": "Mouse", "price": 80},
        {"id": 3, "name": "Teclado", "price": 150}
    ]
    return jsonify(products)


# ==========================
# REGISTRO EN CONSUL
# ==========================
def register_service():
    service_ip = socket.gethostbyname(socket.gethostname())

    payload = {
        "Name": "products",
        "ID": "products-5001",
        "Address": service_ip,
        "Port": 5001,
        "Check": {
            "HTTP": f"http://{service_ip}:5001/health",
            "Interval": "10s"
        }
    }

    requests.put("http://consul:8500/v1/agent/service/register", json=payload)
    print("Products registrado en Consul")


if __name__ == "__main__":
    register_service()
    app.run(host="0.0.0.0", port=5001)

