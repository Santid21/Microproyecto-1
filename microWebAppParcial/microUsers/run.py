from users.views import app
import requests
import socket

# ==========================
# HEALTH
# ==========================
@app.route("/health")
def health():
    return {"status": "healthy"}


# ==========================
# REGISTRO CONSUL
# ==========================
def register_service():
    service_ip = socket.gethostbyname(socket.gethostname())

    payload = {
        "Name": "users",
        "ID": "users-5000",
        "Address": service_ip,
        "Port": 5000,
        "Check": {
            "HTTP": f"http://{service_ip}:5000/health",
            "Interval": "10s"
        }
    }

    requests.put("http://consul:8500/v1/agent/service/register", json=payload)
    print("Users registrado en Consul")


if __name__ == "__main__":
    register_service()
    app.run(host="0.0.0.0", port=5000)

