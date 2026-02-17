from flask import Flask, jsonify, request
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="appuser",
        password="apppassword",
        database="devsecops_db"
    )

@app.route("/")
def home():
    return "Backend is running!"

@app.route("/health")
def health():
    return "OK"

@app.route("/api/services")
def services():
    return jsonify([
        "DevOps Automation",
        "CI/CD Pipelines",
        "Kubernetes Deployments",
        "Cloud Infrastructure"
    ])

@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
        (data["name"], data["email"], data["message"])
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Contact saved successfully"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

