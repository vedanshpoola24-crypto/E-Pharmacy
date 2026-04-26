from datetime import date, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import asc, desc, or_

from app.extensions import db
from app.models import Medicine, StockAdjustment
from app.schemas import MedicineSchema, StockAdjustmentSchema
from app.utils.pagination import paginate, pagination_args
from app.utils.security import audit, min_role_required, validate_json

bp = Blueprint("medicines", __name__, url_prefix="/api/medicines")
schema = MedicineSchema()


def current_user_id():
    identity = get_jwt_identity()
    return int(identity) if isinstance(identity, str) and identity.isdigit() else identity


@bp.get("")
@jwt_required()
def list_medicines():
    page, per_page, search, sort = pagination_args("name")
    query = Medicine.query
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Medicine.name.ilike(like), Medicine.category.ilike(like), Medicine.manufacturer.ilike(like), Medicine.barcode.ilike(like)))
    if request.args.get("low_stock") == "true":
        query = query.filter(Medicine.stock <= Medicine.min_stock)
    if request.args.get("expiring") == "true":
        query = query.filter(Medicine.expiry_date <= date.today() + timedelta(days=30))
    if request.args.get("supplier_id"):
        query = query.filter(Medicine.supplier_id == int(request.args["supplier_id"]))
    column = getattr(Medicine, sort.lstrip("-"), Medicine.name)
    query = query.order_by(desc(column) if sort.startswith("-") else asc(column))
    return jsonify(paginate(query, schema, page, per_page))


@bp.get("/barcode/<barcode>")
@jwt_required()
def by_barcode(barcode):
    return jsonify(schema.dump(Medicine.query.filter_by(barcode=barcode).first_or_404()))


@bp.post("")
@min_role_required("pharmacist")
def create_medicine():
    medicine = Medicine(**validate_json(schema))
    db.session.add(medicine)
    db.session.flush()
    audit("create", "medicine", medicine.id)
    db.session.commit()
    return jsonify(schema.dump(medicine)), 201


@bp.put("/<int:medicine_id>")
@min_role_required("pharmacist")
def update_medicine(medicine_id):
    medicine = Medicine.query.get_or_404(medicine_id)
    for key, value in validate_json(schema, partial=True).items():
        setattr(medicine, key, value)
    audit("update", "medicine", medicine.id)
    db.session.commit()
    return jsonify(schema.dump(medicine))


@bp.post("/<int:medicine_id>/adjust-stock")
@min_role_required("pharmacist")
def adjust_stock(medicine_id):
    medicine = Medicine.query.get_or_404(medicine_id)
    data = validate_json(StockAdjustmentSchema())
    before = medicine.stock
    medicine.stock += data["delta"]
    if medicine.stock < 0:
        return jsonify({"error": "validation_error", "message": "Stock cannot become negative."}), 422
    db.session.add(
        StockAdjustment(
            medicine=medicine,
            user_id=current_user_id(),
            delta=data["delta"],
            reason=data["reason"],
            before_stock=before,
            after_stock=medicine.stock,
        )
    )
    audit("stock_adjust", "medicine", medicine.id, data)
    db.session.commit()
    return jsonify(schema.dump(medicine))


@bp.delete("/<int:medicine_id>")
@min_role_required("admin")
def delete_medicine(medicine_id):
    medicine = Medicine.query.get_or_404(medicine_id)
    audit("delete", "medicine", medicine.id)
    db.session.delete(medicine)
    db.session.commit()
    return "", 204
