from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func

from app.extensions import db
from app.models import Bill, BillItem, Medicine, Payment, StockAdjustment


def money(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def next_invoice_number():
    today = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"INV-{today}-"
    count = Bill.query.filter(Bill.invoice_number.like(f"{prefix}%")).count() + 1
    return f"{prefix}{count:04d}"


def create_bill(data, user_id=None):
    subtotal = Decimal("0.00")
    gst_total = Decimal("0.00")
    discount_total = Decimal("0.00")
    items = []

    bill = Bill(
        invoice_number=next_invoice_number(),
        customer_id=data.get("customer_id"),
        patient_name=data["patient_name"],
        phone=data.get("phone"),
        doctor_name=data.get("doctor_name"),
        prescription_id=data.get("prescription_id"),
        notes=data.get("notes"),
    )
    db.session.add(bill)

    for row in data["items"]:
        medicine = Medicine.query.with_for_update().get(row["medicine_id"])
        if not medicine:
            raise ValueError(f"Medicine {row['medicine_id']} not found.")
        if medicine.stock < row["qty"]:
            raise ValueError(f"Insufficient stock for {medicine.name}. Available: {medicine.stock}.")

        qty = int(row["qty"])
        discount = money(row.get("discount", "0.00"))
        taxable = money(medicine.mrp * qty - discount)
        gst_rate = medicine.gst_rate or Decimal("0")
        gst = money(taxable * gst_rate / Decimal("100"))
        line_total = money(taxable + gst)

        before = medicine.stock
        medicine.stock -= qty
        db.session.add(
            StockAdjustment(
                medicine=medicine,
                user_id=user_id,
                delta=-qty,
                reason=f"Invoice {bill.invoice_number}",
                before_stock=before,
                after_stock=medicine.stock,
            )
        )
        items.append(
            BillItem(
                bill=bill,
                medicine=medicine,
                name=medicine.name,
                batch=medicine.batch,
                qty=qty,
                mrp=money(medicine.mrp),
                gst_rate=gst_rate,
                discount=discount,
                line_total=line_total,
            )
        )
        subtotal += money(medicine.mrp * qty)
        gst_total += gst
        discount_total += discount

    bill.subtotal = money(subtotal)
    bill.gst_total = money(gst_total)
    bill.discount_total = money(discount_total)
    bill.total = money(subtotal - discount_total + gst_total)
    for item in items:
        db.session.add(item)

    paid_total = sum(money(payment["amount"]) for payment in data["payments"])
    if abs(paid_total - bill.total) > Decimal("0.01"):
        raise ValueError(f"Payments must equal bill total {bill.total}.")
    for payment in data["payments"]:
        db.session.add(
            Payment(
                bill=bill,
                mode=payment["mode"],
                amount=money(payment["amount"]),
                reference=payment.get("reference"),
            )
        )
    return bill


def refund_bill(bill, user_id=None):
    if bill.status == "refunded":
        raise ValueError("Bill is already refunded.")
    refund = Bill(
        invoice_number=next_invoice_number(),
        patient_name=bill.patient_name,
        phone=bill.phone,
        doctor_name=bill.doctor_name,
        prescription_id=bill.prescription_id,
        subtotal=-bill.subtotal,
        gst_total=-bill.gst_total,
        discount_total=-bill.discount_total,
        total=-bill.total,
        status="refund",
        original_bill_id=bill.id,
        notes=f"Refund for {bill.invoice_number}",
    )
    db.session.add(refund)
    for item in bill.items:
        if item.medicine:
            before = item.medicine.stock
            item.medicine.stock += item.qty
            db.session.add(
                StockAdjustment(
                    medicine=item.medicine,
                    user_id=user_id,
                    delta=item.qty,
                    reason=f"Refund {bill.invoice_number}",
                    before_stock=before,
                    after_stock=item.medicine.stock,
                )
            )
        db.session.add(
            BillItem(
                bill=refund,
                medicine_id=item.medicine_id,
                name=item.name,
                batch=item.batch,
                qty=-item.qty,
                mrp=item.mrp,
                gst_rate=item.gst_rate,
                discount=-item.discount,
                line_total=-item.line_total,
            )
        )
    db.session.add(Payment(bill=refund, mode="cash", amount=-bill.total, status="refunded"))
    bill.status = "refunded"
    return refund


def sales_summary(start, end):
    rows = (
        db.session.query(func.date(Bill.bill_date), func.sum(Bill.total))
        .filter(Bill.bill_date >= start, Bill.bill_date <= end, Bill.status.in_(["paid", "refund"]))
        .group_by(func.date(Bill.bill_date))
        .all()
    )
    return [{"date": str(day), "total": float(total or 0)} for day, total in rows]
