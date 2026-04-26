from datetime import datetime, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import desc

from app.extensions import db
from app.models import Bill
from app.schemas import BillCreateSchema, BillSchema
from app.services.billing import create_bill, refund_bill
from app.utils.pagination import paginate, pagination_args
from app.utils.security import audit, min_role_required, validate_json

bp = Blueprint("bills", __name__, url_prefix="/api/bills")
schema = BillSchema()


def current_user_id():
    identity = get_jwt_identity()
    return int(identity) if isinstance(identity, str) and identity.isdigit() else identity


@bp.get("")
@jwt_required()
def list_bills():
    page, per_page, search, _ = pagination_args("-bill_date")
    query = Bill.query
    if search:
        query = query.filter(Bill.patient_name.ilike(f"%{search}%") | Bill.invoice_number.ilike(f"%{search}%"))
    query = query.order_by(desc(Bill.bill_date))
    return jsonify(paginate(query, schema, page, per_page))


@bp.get("/<int:bill_id>")
@jwt_required()
def get_bill(bill_id):
    return jsonify(schema.dump(Bill.query.get_or_404(bill_id)))


@bp.post("")
@min_role_required("cashier")
def create():
    try:
        bill = create_bill(validate_json(BillCreateSchema()), current_user_id())
        db.session.flush()
        audit("create", "bill", bill.id, {"invoice_number": bill.invoice_number})
        db.session.commit()
        return jsonify(schema.dump(bill)), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": "validation_error", "message": str(exc)}), 422


@bp.post("/<int:bill_id>/refund")
@min_role_required("cashier")
def refund(bill_id):
    try:
        refund = refund_bill(Bill.query.get_or_404(bill_id), current_user_id())
        db.session.flush()
        audit("refund", "bill", bill_id, {"refund_invoice": refund.invoice_number})
        db.session.commit()
        return jsonify(schema.dump(refund)), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": "validation_error", "message": str(exc)}), 422


@bp.get("/reports/sales")
@jwt_required()
def sales_report():
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    rows = Bill.query.filter(Bill.bill_date >= start, Bill.bill_date <= end).order_by(Bill.bill_date.desc()).all()
    return jsonify(schema.dump(rows, many=True))
