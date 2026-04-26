from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import asc, desc, or_

from app.extensions import db
from app.models import Supplier
from app.schemas import SupplierSchema
from app.utils.pagination import paginate, pagination_args
from app.utils.security import audit, min_role_required, validate_json

bp = Blueprint("suppliers", __name__, url_prefix="/api/suppliers")
schema = SupplierSchema()


@bp.get("")
@jwt_required()
def list_suppliers():
    page, per_page, search, sort = pagination_args("name")
    query = Supplier.query
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Supplier.name.ilike(like), Supplier.contact.ilike(like), Supplier.city.ilike(like)))
    column = getattr(Supplier, sort.lstrip("-"), Supplier.name)
    query = query.order_by(desc(column) if sort.startswith("-") else asc(column))
    return jsonify(paginate(query, schema, page, per_page))


@bp.post("")
@min_role_required("pharmacist")
def create_supplier():
    data = validate_json(schema)
    supplier = Supplier(**data)
    db.session.add(supplier)
    db.session.flush()
    audit("create", "supplier", supplier.id)
    db.session.commit()
    return jsonify(schema.dump(supplier)), 201


@bp.put("/<int:supplier_id>")
@min_role_required("pharmacist")
def update_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    for key, value in validate_json(schema, partial=True).items():
        setattr(supplier, key, value)
    audit("update", "supplier", supplier.id)
    db.session.commit()
    return jsonify(schema.dump(supplier))


@bp.delete("/<int:supplier_id>")
@min_role_required("admin")
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    audit("delete", "supplier", supplier.id)
    db.session.delete(supplier)
    db.session.commit()
    return "", 204
