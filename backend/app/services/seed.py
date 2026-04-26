from datetime import date, timedelta
from decimal import Decimal

from app.extensions import db
from app.models import Customer, Medicine, Prescription, Supplier, User


def seed_demo_data():
    if User.query.first():
        return

    admin = User(name="Admin", email="admin@medstore.local", role="admin")
    admin.set_password("Admin@12345")
    pharmacist = User(name="Pharmacist", email="pharmacist@medstore.local", role="pharmacist")
    pharmacist.set_password("Pharma@12345")
    cashier = User(name="Cashier", email="cashier@medstore.local", role="cashier")
    cashier.set_password("Cashier@12345")

    suppliers = [
        Supplier(name="HealthCare Distributors", contact="Ramesh Patel", phone="+91 98765 43210", email="ramesh@hcd.in", city="Mumbai", gst="27AABCH1234A1Z5", license="MH-DL-2023-001"),
        Supplier(name="MediSupply Co.", contact="Priya Sharma", phone="+91 99887 76655", email="priya@medisupply.in", city="Pune", gst="27AABCM5678B1Z3", license="MH-DL-2023-045"),
        Supplier(name="Pharma Wholesale Ltd", contact="Anil Verma", phone="+91 80001 11222", email="anil@pwl.in", city="Nashik", gst="27AABCP9012C1Z1", license="MH-DL-2023-089"),
    ]
    db.session.add_all([admin, pharmacist, cashier, *suppliers])
    db.session.flush()

    meds = [
        ("890100000001", "Paracetamol 500mg", "Analgesic", "Cipla Ltd", suppliers[0], 365, 500, 100, "2.50", "1.50", "5", False),
        ("890100000002", "Amoxicillin 500mg", "Antibiotic", "Sun Pharma", suppliers[1], 20, 45, 80, "12.00", "8.00", "12", True),
        ("890100000003", "Metformin 500mg", "Antidiabetic", "USV Ltd", suppliers[0], 180, 200, 50, "4.50", "3.00", "5", True),
        ("890100000004", "Atorvastatin 10mg", "Cardiovascular", "Ranbaxy", suppliers[2], 10, 30, 60, "8.00", "5.00", "12", True),
        ("890100000005", "Cetirizine 10mg", "Antihistamine", "Dr Reddys", suppliers[1], 240, 350, 100, "3.00", "1.80", "5", False),
    ]
    for i, row in enumerate(meds, 1):
        barcode, name, category, manufacturer, supplier, days, stock, min_stock, mrp, purchase, gst, rx = row
        db.session.add(
            Medicine(
                barcode=barcode,
                name=name,
                category=category,
                manufacturer=manufacturer,
                supplier=supplier,
                batch=f"BTH24000{i}",
                expiry_date=date.today() + timedelta(days=days),
                stock=stock,
                min_stock=min_stock,
                reorder_quantity=100,
                mrp=Decimal(mrp),
                purchase_price=Decimal(purchase),
                gst_rate=Decimal(gst),
                rx_required=rx,
            )
        )

    customer = Customer(name="Rahul Mehta", phone="+91 99001 12345", age=45)
    db.session.add(customer)
    db.session.add(
        Prescription(
            customer=customer,
            patient_name="Rahul Mehta",
            age=45,
            doctor_name="Dr. Suresh Kumar",
            doctor_reg_no="MH12345",
            issue_date=date.today() - timedelta(days=2),
            valid_until=date.today() + timedelta(days=28),
            medicines_text="Metformin 500mg - 1 tab BD\nAtorvastatin 10mg - 1 tab OD",
            status="active",
        )
    )
    db.session.commit()
