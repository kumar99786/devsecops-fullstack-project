from flask import Flask, jsonify, request
import mysql.connector
from flask_cors import CORS
import os

app = Flask(__name__)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

CORS(app, resources={r"/*": {"origins": origins}})

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
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

