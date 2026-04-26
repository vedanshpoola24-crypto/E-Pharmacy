from datetime import date, datetime, timedelta
from decimal import Decimal

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import Bill, BillItem, Medicine, Supplier

bp = Blueprint("dashboard", __name__, url_prefix="/api")


@bp.get("/dashboard")
@jwt_required()
def dashboard():
    today = date.today()
    low_stock = Medicine.query.filter(Medicine.stock <= Medicine.min_stock).count()
    expiring = Medicine.query.filter(Medicine.expiry_date <= today + timedelta(days=30)).count()
    sales_total = db.session.query(func.coalesce(func.sum(Bill.total), Decimal("0.00"))).filter(Bill.status == "paid").scalar()
    recent_bills = Bill.query.order_by(Bill.bill_date.desc()).limit(5).all()
    return jsonify(
        {
            "total_medicines": Medicine.query.count(),
            "total_suppliers": Supplier.query.count(),
            "low_stock": low_stock,
            "expiring_soon": expiring,
            "sales_total": float(sales_total or 0),
            "recent_bills": [
                {"id": b.id, "invoice_number": b.invoice_number, "patient_name": b.patient_name, "total": float(b.total), "bill_date": b.bill_date.isoformat()}
                for b in recent_bills
            ],
        }
    )


@bp.get("/reports/analytics")
@jwt_required()
def analytics():
    today = datetime.utcnow()
    start = today - timedelta(days=30)
    daily = (
        db.session.query(func.date(Bill.bill_date), func.coalesce(func.sum(Bill.total), Decimal("0.00")))
        .filter(Bill.bill_date >= start)
        .group_by(func.date(Bill.bill_date))
        .order_by(func.date(Bill.bill_date))
        .all()
    )
    top = (
        db.session.query(BillItem.name, func.coalesce(func.sum(BillItem.qty), 0).label("qty"))
        .group_by(BillItem.name)
        .order_by(func.sum(BillItem.qty).desc())
        .limit(8)
        .all()
    )
    profit = (
        db.session.query(func.coalesce(func.sum((BillItem.mrp - Medicine.purchase_price) * BillItem.qty), Decimal("0.00")))
        .join(Medicine, Medicine.id == BillItem.medicine_id)
        .scalar()
    )
    gst = db.session.query(func.coalesce(func.sum(Bill.gst_total), Decimal("0.00"))).scalar()
    expired = Medicine.query.filter(Medicine.expiry_date < date.today()).count()
    return jsonify(
        {
            "sales": [{"date": str(day), "total": float(total or 0)} for day, total in daily],
            "top_selling": [{"name": name, "qty": int(qty or 0)} for name, qty in top],
            "profit_loss": {"gross_profit": float(profit or 0)},
            "gst_report": {"gst_collected": float(gst or 0)},
            "inventory_report": {"expired": expired, "low_stock": Medicine.query.filter(Medicine.stock <= Medicine.min_stock).count()},
        }
    )


@bp.get("/reports/supplier-wise")
@jwt_required()
def supplier_report():
    rows = (
        db.session.query(Supplier.name, func.count(Medicine.id), func.coalesce(func.sum(Medicine.stock), 0))
        .outerjoin(Medicine)
        .group_by(Supplier.id)
        .order_by(Supplier.name)
        .all()
    )
    return jsonify([{"supplier": name, "medicine_count": count, "stock_units": int(stock or 0)} for name, count, stock in rows])
