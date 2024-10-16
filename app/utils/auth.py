import jwt
from flask import request, jsonify, current_app
from functools import wraps
from datetime import datetime, timedelta, timezone
from ..models import User, Role
from ..extensions import db
from dotenv import load_dotenv
import os

load_dotenv()


def generate_jwt(user):
    """Generate a JWT token for a user."""
    roles = [role.role_name for role in user.roles]
    payload = {
        "user_id": user.id,
        "roles": roles,  # Store the roles as a list in the payload
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token


def decode_jwt(token):
    """Decode a JWT token."""
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def admin_required(f):
    """Decorator to check if the user has an 'admin/super' role."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        token = token.split(" ")[1]  # Assume token is in the format "Bearer <token>"
        payload = decode_jwt(token)

        if not payload:
            return jsonify({"message": "Invalid or expired token"}), 403

        # Check if 'admin' or 'super' is in the user's roles
        if not any(role in payload.get("roles", []) for role in ["admin", "super"]):
            return jsonify({"message": "Admin or Super access required"}), 403

        return f(*args, **kwargs)

    return decorated_function
