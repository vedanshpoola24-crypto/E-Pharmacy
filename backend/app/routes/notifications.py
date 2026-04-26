from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import Notification
from app.schemas import NotificationSchema
from app.services.notifications import refresh_inventory_alerts, send_email_alert, send_sms_alert
from app.utils.security import min_role_required

bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")
schema = NotificationSchema()


@bp.get("")
@jwt_required()
def list_notifications():
    notes = Notification.query.order_by(Notification.created_at.desc()).limit(100).all()
    return jsonify(schema.dump(notes, many=True))


@bp.post("/refresh-alerts")
@min_role_required("pharmacist")
def refresh_alerts():
    result = refresh_inventory_alerts()
    db.session.commit()
    return jsonify(result)


@bp.post("/<int:notification_id>/read")
@jwt_required()
def mark_read(notification_id):
    note = Notification.query.get_or_404(notification_id)
    note.is_read = True
    db.session.commit()
    return jsonify(schema.dump(note))


@bp.post("/<int:notification_id>/send")
@min_role_required("pharmacist")
def send(notification_id):
    note = Notification.query.get_or_404(notification_id)
    email = send_email_alert(note)
    sms = send_sms_alert(note)
    return jsonify({"email": email, "sms": sms})
