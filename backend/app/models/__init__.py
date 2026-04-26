from datetime import datetime
from decimal import Decimal
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="pharmacist")
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Supplier(TimestampMixin, db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False, index=True)
    contact = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    city = db.Column(db.String(120))
    gst = db.Column(db.String(30))
    license = db.Column(db.String(80))

    medicines = db.relationship("Medicine", back_populates="supplier", lazy="dynamic")


class Medicine(TimestampMixin, db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    manufacturer = db.Column(db.String(160))
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id", ondelete="SET NULL"), index=True)
    barcode = db.Column(db.String(80), unique=True, index=True)
    batch = db.Column(db.String(80), index=True)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    stock = db.Column(db.Integer, nullable=False, default=0)
    min_stock = db.Column(db.Integer, nullable=False, default=50)
    reorder_quantity = db.Column(db.Integer, nullable=False, default=100)
    mrp = db.Column(db.Numeric(10, 2), nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), default=Decimal("0.00"))
    gst_rate = db.Column(db.Numeric(5, 2), default=Decimal("0.00"))
    rx_required = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text)

    supplier = db.relationship("Supplier", back_populates="medicines")
    bill_items = db.relationship("BillItem", back_populates="medicine")
    adjustments = db.relationship("StockAdjustment", back_populates="medicine", cascade="all, delete-orphan")


class Customer(TimestampMixin, db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    phone = db.Column(db.String(50), index=True)
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    age = db.Column(db.Integer)

    prescriptions = db.relationship("Prescription", back_populates="customer")
    bills = db.relationship("Bill", back_populates="customer")


class Prescription(TimestampMixin, db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    patient_name = db.Column(db.String(160), nullable=False, index=True)
    age = db.Column(db.Integer)
    doctor_name = db.Column(db.String(160), nullable=False)
    doctor_reg_no = db.Column(db.String(80))
    issue_date = db.Column(db.Date, nullable=False)
    valid_until = db.Column(db.Date)
    medicines_text = db.Column(db.Text)
    notes = db.Column(db.Text)
    status = db.Column(db.String(30), nullable=False, default="active")
    file_path = db.Column(db.String(255))
    ocr_text = db.Column(db.Text)
    verified_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))

    customer = db.relationship("Customer", back_populates="prescriptions")
    bills = db.relationship("Bill", back_populates="prescription")


class Bill(TimestampMixin, db.Model):
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(40), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    patient_name = db.Column(db.String(160), nullable=False, index=True)
    phone = db.Column(db.String(50))
    doctor_name = db.Column(db.String(160))
    prescription_id = db.Column(db.Integer, db.ForeignKey("prescriptions.id", ondelete="SET NULL"))
    bill_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    gst_total = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    discount_total = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    status = db.Column(db.String(30), nullable=False, default="paid")
    original_bill_id = db.Column(db.Integer, db.ForeignKey("bills.id", ondelete="SET NULL"))
    notes = db.Column(db.Text)

    customer = db.relationship("Customer", back_populates="bills")
    prescription = db.relationship("Prescription", back_populates="bills")
    items = db.relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")
    payments = db.relationship("Payment", back_populates="bill", cascade="all, delete-orphan")


class BillItem(TimestampMixin, db.Model):
    __tablename__ = "bill_items"

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id", ondelete="CASCADE"), nullable=False, index=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id", ondelete="SET NULL"), index=True)
    name = db.Column(db.String(180), nullable=False)
    batch = db.Column(db.String(80))
    qty = db.Column(db.Integer, nullable=False)
    mrp = db.Column(db.Numeric(10, 2), nullable=False)
    gst_rate = db.Column(db.Numeric(5, 2), default=Decimal("0.00"))
    discount = db.Column(db.Numeric(10, 2), default=Decimal("0.00"))
    line_total = db.Column(db.Numeric(10, 2), nullable=False)

    bill = db.relationship("Bill", back_populates="items")
    medicine = db.relationship("Medicine", back_populates="bill_items")


class Payment(TimestampMixin, db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id", ondelete="CASCADE"), nullable=False, index=True)
    mode = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    reference = db.Column(db.String(120))
    status = db.Column(db.String(30), default="captured", nullable=False)

    bill = db.relationship("Bill", back_populates="payments")


class Notification(TimestampMixin, db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(40), nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    channel = db.Column(db.String(30), nullable=False, default="in_app")
    recipient = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    severity = db.Column(db.String(20), default="info", nullable=False)


class AuditLog(TimestampMixin, db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action = db.Column(db.String(80), nullable=False)
    entity = db.Column(db.String(80), nullable=False)
    entity_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(80))


class StockAdjustment(TimestampMixin, db.Model):
    __tablename__ = "stock_adjustments"

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    delta = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(160), nullable=False)
    before_stock = db.Column(db.Integer, nullable=False)
    after_stock = db.Column(db.Integer, nullable=False)

    medicine = db.relationship("Medicine", back_populates="adjustments")
