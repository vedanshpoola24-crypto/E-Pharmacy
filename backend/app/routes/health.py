from flask import Blueprint, jsonify
from sqlalchemy import text
from app.extensions import db

bp = Blueprint("health", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    db_ok = False
    try:
        db.session.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        print(f"Database health check failed: {e}")

    return jsonify({
        "status": "ok" if db_ok else "error",
        "service": "medstore-api",
        "database": "connected" if db_ok else "disconnected"
    }), 200 if db_ok else 500
