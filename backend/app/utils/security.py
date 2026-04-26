from functools import wraps

from flask import jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
from marshmallow import ValidationError
import bleach

from app.extensions import db
from app.models import AuditLog


ROLE_ORDER = {"cashier": 1, "pharmacist": 2, "admin": 3}


def clean_string(value):
    if value is None:
        return value
    if isinstance(value, str):
        return bleach.clean(value.strip(), tags=[], attributes={}, strip=True)
    return value


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if roles and role not in roles:
                return jsonify({"error": "forbidden", "message": "Insufficient role"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def min_role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            role = get_jwt().get("role")
            if ROLE_ORDER.get(role, 0) < ROLE_ORDER.get(required_role, 99):
                return jsonify({"error": "forbidden", "message": "Insufficient role"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def audit(action, entity, entity_id=None, details=None):
    try:
        user_id = get_jwt_identity()
    except Exception:
        user_id = None
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    db.session.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=details or {},
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        )
    )


def validate_json(schema, partial=False):
    json_data = request.get_json(silent=True)
    if json_data is None:
        raise ValidationError({"json": ["Request body must be valid JSON."]})
    return schema.load(json_data, partial=partial)
