from marshmallow import Schema, ValidationError, fields, post_load, pre_load, validates, validates_schema

from app.utils.security import clean_string


class CleanSchema(Schema):
    @pre_load
    def blank_to_none(self, data, **kwargs):
        return {key: (None if value == "" else value) for key, value in data.items()}

    @post_load
    def clean(self, data, **kwargs):
        return {key: clean_string(value) for key, value in data.items()}


class UserSchema(CleanSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    role = fields.Str(load_default="pharmacist")
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    @validates("role")
    def validate_role(self, value, **kwargs):
        if value not in {"admin", "pharmacist", "cashier"}:
            raise ValidationError("Role must be admin, pharmacist, or cashier.")


class LoginSchema(CleanSchema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class SupplierSchema(CleanSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    contact = fields.Str(required=True)
    phone = fields.Str(required=True)
    email = fields.Email(allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    gst = fields.Str(allow_none=True)
    license = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class MedicineSchema(CleanSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    manufacturer = fields.Str(allow_none=True)
    supplier_id = fields.Int(allow_none=True)
    supplier_name = fields.Method("get_supplier_name", dump_only=True)
    barcode = fields.Str(allow_none=True)
    batch = fields.Str(allow_none=True)
    expiry_date = fields.Date(required=True)
    stock = fields.Int(required=True)
    min_stock = fields.Int(load_default=50)
    reorder_quantity = fields.Int(load_default=100)
    mrp = fields.Decimal(required=True, as_string=True)
    purchase_price = fields.Decimal(load_default="0.00", as_string=True)
    gst_rate = fields.Decimal(load_default="0.00", as_string=True)
    rx_required = fields.Bool(load_default=False)
    description = fields.Str(allow_none=True)
    status = fields.Method("get_status", dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else None

    def get_status(self, obj):
        if obj.stock <= obj.min_stock:
            return "low_stock"
        return "ok"


class StockAdjustmentSchema(CleanSchema):
    delta = fields.Int(required=True)
    reason = fields.Str(required=True)


class CustomerSchema(CleanSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    phone = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    address = fields.Str(allow_none=True)
    age = fields.Int(allow_none=True)


class PrescriptionSchema(CleanSchema):
    id = fields.Int(dump_only=True)
    customer_id = fields.Int(allow_none=True)
    patient_name = fields.Str(required=True)
    age = fields.Int(allow_none=True)
    doctor_name = fields.Str(required=True)
    doctor_reg_no = fields.Str(allow_none=True)
    issue_date = fields.Date(required=True)
    valid_until = fields.Date(allow_none=True)
    medicines_text = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    status = fields.Str(load_default="active")
    file_path = fields.Str(dump_only=True)
    ocr_text = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class BillItemInputSchema(CleanSchema):
    medicine_id = fields.Int(required=True)
    qty = fields.Int(required=True)
    discount = fields.Decimal(load_default="0.00", as_string=True)

    @validates("qty")
    def validate_qty(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Quantity must be greater than zero.")


class PaymentInputSchema(CleanSchema):
    mode = fields.Str(required=True)
    amount = fields.Decimal(required=True, as_string=True)
    reference = fields.Str(allow_none=True)

    @validates("mode")
    def validate_mode(self, value, **kwargs):
        if value not in {"cash", "card", "upi"}:
            raise ValidationError("Payment mode must be cash, card, or upi.")


class BillCreateSchema(CleanSchema):
    customer_id = fields.Int(allow_none=True)
    patient_name = fields.Str(required=True)
    phone = fields.Str(allow_none=True)
    doctor_name = fields.Str(allow_none=True)
    prescription_id = fields.Int(allow_none=True)
    items = fields.List(fields.Nested(BillItemInputSchema), required=True)
    payments = fields.List(fields.Nested(PaymentInputSchema), required=True)
    notes = fields.Str(allow_none=True)

    @validates_schema
    def validate_items(self, data, **kwargs):
        if not data.get("items"):
            raise ValidationError("Bill must contain at least one item.", "items")


class BillItemSchema(CleanSchema):
    id = fields.Int()
    medicine_id = fields.Int()
    name = fields.Str()
    batch = fields.Str()
    qty = fields.Int()
    mrp = fields.Decimal(as_string=True)
    gst_rate = fields.Decimal(as_string=True)
    discount = fields.Decimal(as_string=True)
    line_total = fields.Decimal(as_string=True)


class PaymentSchema(CleanSchema):
    id = fields.Int()
    mode = fields.Str()
    amount = fields.Decimal(as_string=True)
    reference = fields.Str()
    status = fields.Str()


class BillSchema(CleanSchema):
    id = fields.Int()
    invoice_number = fields.Str()
    patient_name = fields.Str()
    phone = fields.Str()
    doctor_name = fields.Str()
    prescription_id = fields.Int()
    bill_date = fields.DateTime()
    subtotal = fields.Decimal(as_string=True)
    gst_total = fields.Decimal(as_string=True)
    discount_total = fields.Decimal(as_string=True)
    total = fields.Decimal(as_string=True)
    status = fields.Str()
    notes = fields.Str()
    items = fields.Nested(BillItemSchema, many=True)
    payments = fields.Nested(PaymentSchema, many=True)


class NotificationSchema(CleanSchema):
    id = fields.Int()
    type = fields.Str()
    title = fields.Str()
    message = fields.Str()
    channel = fields.Str()
    severity = fields.Str()
    is_read = fields.Bool()
    created_at = fields.DateTime()


class ChatSchema(CleanSchema):
    message = fields.Str(required=True)
