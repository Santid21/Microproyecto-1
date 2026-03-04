from flask import Flask, jsonify
import requests
import socket

app = Flask(__name__)

# ==========================
# HEALTH
# ==========================
@app.route("/health")
def health():
    return {"status": "healthy"}


# ==========================
# DESCUBRIMIENTO CONSUL
# ==========================
def discover_products():
    response = requests.get("http://consul:8500/v1/catalog/service/products")
    data = response.json()

    if not data:
        return None

    service = data[0]
    return f"http://{service['ServiceAddress']}:{service['ServicePort']}"


# ==========================
# ENDPOINTS
# ==========================
@app.route("/")
def home():
    return {"message": "MicroOrders funcionando"}


@app.route("/api/orders")
def get_orders():
    products_url = discover_products()

    if not products_url:
        return {"error": "Products service not found"}, 500

    products_response = requests.get(f"{products_url}/api/products")
    products = products_response.json()

    return jsonify({
        "message": "Orden creada",
        "productos_disponibles": products
    })


# ==========================
# REGISTRO CONSUL
# ==========================
def register_service():
    service_ip = socket.gethostbyname(socket.gethostname())

    payload = {
        "Name": "orders",
        "ID": "orders-5002",
        "Address": service_ip,
        "Port": 5002,
        "Check": {
            "HTTP": f"http://{service_ip}:5002/health",
            "Interval": "10s"
        }
    }

    requests.put("http://consul:8500/v1/agent/service/register", json=payload)
    print("Orders registrado en Consul")


if __name__ == "__main__":
    register_service()
    app.run(host="0.0.0.0", port=5002)

