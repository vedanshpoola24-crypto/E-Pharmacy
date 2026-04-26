from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import Customer
from app.schemas import CustomerSchema
from app.utils.pagination import paginate, pagination_args
from app.utils.security import min_role_required, validate_json

bp = Blueprint("customers", __name__, url_prefix="/api/customers")
schema = CustomerSchema()


@bp.get("")
@jwt_required()
def list_customers():
    page, per_page, search, _ = pagination_args("name")
    query = Customer.query
    if search:
        query = query.filter(Customer.name.ilike(f"%{search}%") | Customer.phone.ilike(f"%{search}%"))
    return jsonify(paginate(query.order_by(Customer.name), schema, page, per_page))


@bp.post("")
@min_role_required("cashier")
def create_customer():
    customer = Customer(**validate_json(schema))
    db.session.add(customer)
    db.session.commit()
    return jsonify(schema.dump(customer)), 201
