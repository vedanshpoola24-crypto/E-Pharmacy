"""initial production schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-04-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("contact", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255)),
        sa.Column("address", sa.Text()),
        sa.Column("city", sa.String(length=120)),
        sa.Column("gst", sa.String(length=30)),
        sa.Column("license", sa.String(length=80)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_suppliers_name", "suppliers", ["name"])

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("phone", sa.String(length=50)),
        sa.Column("email", sa.String(length=255)),
        sa.Column("address", sa.Text()),
        sa.Column("age", sa.Integer()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_customers_name", "customers", ["name"])
    op.create_index("ix_customers_phone", "customers", ["phone"])

    op.create_table(
        "medicines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("manufacturer", sa.String(length=160)),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id", ondelete="SET NULL")),
        sa.Column("barcode", sa.String(length=80), unique=True),
        sa.Column("batch", sa.String(length=80)),
        sa.Column("expiry_date", sa.Date(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("min_stock", sa.Integer(), nullable=False),
        sa.Column("reorder_quantity", sa.Integer(), nullable=False),
        sa.Column("mrp", sa.Numeric(10, 2), nullable=False),
        sa.Column("purchase_price", sa.Numeric(10, 2)),
        sa.Column("gst_rate", sa.Numeric(5, 2)),
        sa.Column("rx_required", sa.Boolean(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    for name, cols in {
        "ix_medicines_name": ["name"],
        "ix_medicines_category": ["category"],
        "ix_medicines_supplier_id": ["supplier_id"],
        "ix_medicines_barcode": ["barcode"],
        "ix_medicines_batch": ["batch"],
        "ix_medicines_expiry_date": ["expiry_date"],
    }.items():
        op.create_index(name, "medicines", cols)

    op.create_table(
        "prescriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL")),
        sa.Column("patient_name", sa.String(length=160), nullable=False),
        sa.Column("age", sa.Integer()),
        sa.Column("doctor_name", sa.String(length=160), nullable=False),
        sa.Column("doctor_reg_no", sa.String(length=80)),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date()),
        sa.Column("medicines_text", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("file_path", sa.String(length=255)),
        sa.Column("ocr_text", sa.Text()),
        sa.Column("verified_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_prescriptions_customer_id", "prescriptions", ["customer_id"])
    op.create_index("ix_prescriptions_patient_name", "prescriptions", ["patient_name"])

    op.create_table(
        "bills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("invoice_number", sa.String(length=40), nullable=False, unique=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL")),
        sa.Column("patient_name", sa.String(length=160), nullable=False),
        sa.Column("phone", sa.String(length=50)),
        sa.Column("doctor_name", sa.String(length=160)),
        sa.Column("prescription_id", sa.Integer(), sa.ForeignKey("prescriptions.id", ondelete="SET NULL")),
        sa.Column("bill_date", sa.DateTime(), nullable=False),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.Column("gst_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("discount_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("total", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("original_bill_id", sa.Integer(), sa.ForeignKey("bills.id", ondelete="SET NULL")),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_bills_invoice_number", "bills", ["invoice_number"])
    op.create_index("ix_bills_customer_id", "bills", ["customer_id"])
    op.create_index("ix_bills_patient_name", "bills", ["patient_name"])
    op.create_index("ix_bills_bill_date", "bills", ["bill_date"])

    op.create_table(
        "bill_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bill_id", sa.Integer(), sa.ForeignKey("bills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("medicine_id", sa.Integer(), sa.ForeignKey("medicines.id", ondelete="SET NULL")),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("batch", sa.String(length=80)),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("mrp", sa.Numeric(10, 2), nullable=False),
        sa.Column("gst_rate", sa.Numeric(5, 2)),
        sa.Column("discount", sa.Numeric(10, 2)),
        sa.Column("line_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_bill_items_bill_id", "bill_items", ["bill_id"])
    op.create_index("ix_bill_items_medicine_id", "bill_items", ["medicine_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bill_id", sa.Integer(), sa.ForeignKey("bills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode", sa.String(length=30), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("reference", sa.String(length=120)),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_payments_bill_id", "payments", ["bill_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("channel", sa.String(length=30), nullable=False),
        sa.Column("recipient", sa.String(length=255)),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_notifications_type", "notifications", ["type"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("entity", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.Integer()),
        sa.Column("details", sa.JSON()),
        sa.Column("ip_address", sa.String(length=80)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])

    op.create_table(
        "stock_adjustments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("medicine_id", sa.Integer(), sa.ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=160), nullable=False),
        sa.Column("before_stock", sa.Integer(), nullable=False),
        sa.Column("after_stock", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_stock_adjustments_medicine_id", "stock_adjustments", ["medicine_id"])


def downgrade():
    for table in [
        "stock_adjustments",
        "audit_logs",
        "notifications",
        "payments",
        "bill_items",
        "bills",
        "prescriptions",
        "medicines",
        "customers",
        "suppliers",
        "users",
    ]:
        op.drop_table(table)
