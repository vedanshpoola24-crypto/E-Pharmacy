import os
from datetime import date

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Prescription
from app.schemas import PrescriptionSchema
from app.services.notifications import create_notification
from app.services.ocr import extract_text_from_file
from app.utils.pagination import paginate, pagination_args
from app.utils.security import audit, min_role_required, validate_json

bp = Blueprint("prescriptions", __name__, url_prefix="/api/prescriptions")
schema = PrescriptionSchema()


def current_user_id():
    identity = get_jwt_identity()
    return int(identity) if isinstance(identity, str) and identity.isdigit() else identity


@bp.get("")
@jwt_required()
def list_prescriptions():
    page, per_page, search, _ = pagination_args("-created_at")
    query = Prescription.query
    if search:
        like = f"%{search}%"
        query = query.filter(Prescription.patient_name.ilike(like) | Prescription.doctor_name.ilike(like))
    return jsonify(paginate(query.order_by(Prescription.created_at.desc()), schema, page, per_page))


@bp.post("")
@min_role_required("pharmacist")
def create_prescription():
    data = request.form.to_dict() if request.form else validate_json(schema)
    loaded = schema.load(data)
    rx = Prescription(**loaded)
    upload = request.files.get("file")
    if upload:
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        filename = secure_filename(upload.filename)
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        upload.save(path)
        rx.file_path = path
        rx.ocr_text = extract_text_from_file(path)
    if rx.valid_until and rx.valid_until < date.today():
        rx.status = "expired"
    db.session.add(rx)
    db.session.flush()
    create_notification("prescription", "New prescription uploaded", f"{rx.patient_name} prescription needs review.", "info")
    audit("create", "prescription", rx.id)
    db.session.commit()
    return jsonify(schema.dump(rx)), 201


@bp.post("/<int:rx_id>/verify")
@min_role_required("pharmacist")
def verify_prescription(rx_id):
    rx = Prescription.query.get_or_404(rx_id)
    rx.status = "verified"
    rx.verified_by = current_user_id()
    audit("verify", "prescription", rx.id)
    db.session.commit()
    return jsonify(schema.dump(rx))


@bp.delete("/<int:rx_id>")
@min_role_required("admin")
def delete_prescription(rx_id):
    rx = Prescription.query.get_or_404(rx_id)
    audit("delete", "prescription", rx.id)
    db.session.delete(rx)
    db.session.commit()
    return "", 204
