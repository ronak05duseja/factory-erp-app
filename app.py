"""
FACTORY ERP - minimal demo app
Covers the two epics tracked in Jira:
  - User Authentication (FE-6, FE-9, FE-11)
  - Inventory Management (FE-7, FE-12)

In-memory storage only. This is a demo for the ASDD experiment,
not a production app - no real password hashing persistence,
no real database.
"""

import re
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = "demo-secret-key-change-me"

# ---- In-memory "database" ----
users = {}       # username -> {"password": str}
inventory = {     # product -> quantity
    "widget-a": 42,
    "widget-b": 3,
    "widget-c": 15,
}
LOW_STOCK_THRESHOLD = 5


def is_strong_password(pw: str) -> bool:
    """FE-10: password must be 8+ chars, include a digit and a letter."""
    if len(pw) < 8:
        return False
    if not re.search(r"[A-Za-z]", pw):
        return False
    if not re.search(r"\d", pw):
        return False
    return True


# ---------------------------------------------------------------------
# FE-9: Register a new user account with email and password
# ---------------------------------------------------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    # FE-10: password strength validation on signup
    if not is_strong_password(password):
        return jsonify({
            "error": "Password must be at least 8 characters and include "
                     "both a letter and a number."
        }), 400

    if username in users:
        return jsonify({"error": "username already exists"}), 409

    users[username] = {"password": password}
    return jsonify({"message": f"user '{username}' registered"}), 201


# ---------------------------------------------------------------------
# FE-11: Login and logout with session handling
# FE-6: Add the error message for incomplete/incorrect password
# ---------------------------------------------------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Please enter both username and password."}), 400

    user = users.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Incorrect username or password."}), 401

    session["username"] = username
    return jsonify({"message": f"welcome back, {username}"}), 200


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return jsonify({"message": "logged out"}), 200


def _require_login():
    return "username" in session


# ---------------------------------------------------------------------
# FE-7: View current stock levels for all products
# ---------------------------------------------------------------------
@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    if not _require_login():
        return jsonify({"error": "login required"}), 401
    return jsonify(inventory), 200


# ---------------------------------------------------------------------
# FE-12: Add low-stock alert when quantity falls below threshold
# ---------------------------------------------------------------------
@app.route("/api/inventory/low-stock", methods=["GET"])
def low_stock():
    if not _require_login():
        return jsonify({"error": "login required"}), 401
    low = {p: q for p, q in inventory.items() if q < LOW_STOCK_THRESHOLD}
    return jsonify({"threshold": LOW_STOCK_THRESHOLD, "low_stock_items": low}), 200


if __name__ == "__main__":
    app.run(debug=True)
