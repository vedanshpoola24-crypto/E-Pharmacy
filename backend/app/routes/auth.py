from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db, limiter
from app.models import User
from app.schemas import LoginSchema, UserSchema
from app.utils.security import audit, validate_json

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
@jwt_required(optional=True)
def register():
    data = validate_json(UserSchema())
    current = get_jwt_identity()
    if current and data.get("role") == "admin":
        user = User.query.get(current)
        if not user or user.role != "admin":
            return jsonify({"error": "forbidden", "message": "Only admins can create admins."}), 403
    elif data.get("role") == "admin" and User.query.filter_by(role="admin").first():
        return jsonify({"error": "forbidden", "message": "Admin already exists."}), 403

    user = User(name=data["name"], email=data["email"].lower(), role=data.get("role", "pharmacist"))
    user.set_password(data["password"])
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "conflict", "message": "Email already registered."}), 409
    audit("register", "user", user.id)
    db.session.commit()
    return jsonify(UserSchema(exclude=("password",)).dump(user)), 201


@bp.post("/login")
@limiter.limit("10 per minute")
def login():
    data = validate_json(LoginSchema())
    user = User.query.filter_by(email=data["email"].lower(), is_active=True).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "unauthorized", "message": "Invalid credentials."}), 401
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "email": user.email})
    audit("login", "user", user.id)
    db.session.commit()
    return jsonify({"access_token": token, "user": UserSchema(exclude=("password",)).dump(user)})


@bp.post("/logout")
@jwt_required()
def logout():
    audit("logout", "user", get_jwt_identity())
    db.session.commit()
    return jsonify({"message": "Logged out. Remove the token client-side."})


@bp.get("/me")
@jwt_required()
def me():
    return jsonify(UserSchema(exclude=("password",)).dump(User.query.get_or_404(get_jwt_identity())))
