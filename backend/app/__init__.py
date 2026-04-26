import sqlite3
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from app.config import Config
from app.extensions import cors, db, jwt, limiter, migrate
from app.models import Bill, BillItem, Customer, Medicine, Prescription, Supplier
from app.routes import register_blueprints
from app.services.seed import seed_demo_data


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=False)
    limiter.init_app(app)
    register_blueprints(app)
    register_handlers(app)
    register_commands(app)
    register_security_headers(app)
    register_csrf_origin_check(app)
    return app


def register_security_headers(app):
    @app.after_request
    def secure_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if not app.debug:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response


def register_csrf_origin_check(app):
    @app.before_request
    def csrf_origin_check():
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.path.startswith("/api/"):
            origin = request.headers.get("Origin")
            allowed = set(app.config["CORS_ORIGINS"])
            if origin and origin not in allowed:
                return jsonify({"error": "csrf_blocked", "message": "Request origin is not allowed."}), 403


def register_handlers(app):
    @app.errorhandler(ValidationError)
    def validation_error(error):
        return jsonify({"error": "validation_error", "messages": error.messages}), 422

    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        db.session.rollback()
        return jsonify({"error": "conflict", "message": "Database constraint failed."}), 409

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify({"error": error.name.lower().replace(" ", "_"), "message": error.description}), error.code

    @app.errorhandler(Exception)
    def unexpected_error(error):
        db.session.rollback()
        app.logger.exception(error)
        return jsonify({"error": "server_error", "message": "Unexpected server error."}), 500


def register_commands(app):
    @app.cli.command("seed")
    def seed():
        db.create_all()
        seed_demo_data()
        print("Seeded demo users, suppliers, medicines, and prescriptions.")

    @app.cli.command("import-sqlite")
    def import_sqlite():
        path = app.config.get("SQLITE_IMPORT_PATH", "medstore.db")
        import_legacy_sqlite(path)
        print(f"Imported legacy SQLite data from {path}.")


def import_legacy_sqlite(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    suppliers = {}
    for row in conn.execute("SELECT * FROM suppliers"):
        supplier = Supplier(
            name=row["name"],
            contact=row["contact"],
            phone=row["phone"],
            email=row["email"],
            address=row["address"],
            city=row["city"],
            gst=row["gst"],
            license=row["license"],
        )
        db.session.add(supplier)
        db.session.flush()
        suppliers[row["id"]] = supplier.id

    medicines = {}
    for row in conn.execute("SELECT * FROM medicines"):
        medicine = Medicine(
            name=row["name"],
            category=row["category"],
            manufacturer=row["manufacturer"],
            supplier_id=suppliers.get(row["supplier_id"]),
            batch=row["batch"],
            expiry_date=datetime.strptime(row["expiry"], "%Y-%m-%d").date(),
            stock=row["stock"],
            min_stock=row["min_stock"],
            mrp=row["mrp"],
            purchase_price=row["purchase"],
            gst_rate=row["gst"],
            rx_required=bool(row["rx"]),
            description=row["description"],
        )
        db.session.add(medicine)
        db.session.flush()
        medicines[row["id"]] = medicine.id

    prescriptions = {}
    for row in conn.execute("SELECT * FROM prescriptions"):
        rx = Prescription(
            patient_name=row["patient"],
            age=row["age"],
            doctor_name=row["doctor"],
            doctor_reg_no=row["regno"],
            issue_date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
            valid_until=datetime.strptime(row["valid"], "%Y-%m-%d").date() if row["valid"] else None,
            medicines_text=row["meds"],
            notes=row["notes"],
            status=row["status"],
        )
        db.session.add(rx)
        db.session.flush()
        prescriptions[row["id"]] = rx.id

    for row in conn.execute("SELECT * FROM bills"):
        customer = Customer.query.filter_by(name=row["patient"], phone=row["phone"]).first()
        if not customer:
            customer = Customer(name=row["patient"], phone=row["phone"])
            db.session.add(customer)
            db.session.flush()
        bill = Bill(
            invoice_number=f"LEGACY-{row['id']:06d}",
            customer_id=customer.id,
            patient_name=row["patient"],
            phone=row["phone"],
            doctor_name=row["doctor"],
            prescription_id=prescriptions.get(row["rx_id"]),
            bill_date=datetime.strptime(row["date"], "%Y-%m-%d"),
            total=row["total"],
            subtotal=row["total"],
            status="paid",
        )
        db.session.add(bill)
        db.session.flush()
        for item in conn.execute("SELECT * FROM bill_items WHERE bill_id=?", (row["id"],)):
            db.session.add(
                BillItem(
                    bill=bill,
                    medicine_id=medicines.get(item["med_id"]),
                    name=item["name"],
                    qty=item["qty"],
                    mrp=item["mrp"],
                    gst_rate=0,
                    discount=0,
                    line_total=item["qty"] * item["mrp"],
                )
            )
    db.session.commit()
    conn.close()
