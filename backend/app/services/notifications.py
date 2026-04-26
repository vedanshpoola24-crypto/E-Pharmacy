from datetime import date, timedelta

from app.extensions import db
from app.models import Medicine, Notification


def create_notification(type_, title, message, severity="info", channel="in_app", recipient=None):
    note = Notification(
        type=type_,
        title=title,
        message=message,
        severity=severity,
        channel=channel,
        recipient=recipient,
    )
    db.session.add(note)
    return note


def refresh_inventory_alerts():
    low_stock = Medicine.query.filter(Medicine.stock <= Medicine.min_stock).all()
    expiring = Medicine.query.filter(Medicine.expiry_date <= date.today() + timedelta(days=30)).all()
    for med in low_stock:
        create_notification(
            "low_stock",
            f"Low stock: {med.name}",
            f"{med.name} has {med.stock} units left. Reorder {med.reorder_quantity} units.",
            "warning",
        )
    for med in expiring:
        create_notification(
            "expiry",
            f"Expiring soon: {med.name}",
            f"Batch {med.batch or 'N/A'} expires on {med.expiry_date.isoformat()}.",
            "danger",
        )
    return {"low_stock": len(low_stock), "expiring": len(expiring)}


def send_email_alert(notification):
    return {"queued": True, "channel": "email", "notification_id": notification.id}


def send_sms_alert(notification):
    return {"queued": True, "channel": "sms", "notification_id": notification.id}
