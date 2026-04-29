from datetime import date, datetime, timedelta
import random
from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models import Supplier, Medicine, Customer, Prescription, Bill, BillItem, Notification, Payment

app = create_app()

def seed_more_data():
    with app.app_context():
        # 1. Add more suppliers
        suppliers_data = [
            ("Apollo Pharmacies", "Sunil Reddy", "+91 98765 00001", "contact@apollo.in", "Hyderabad", "36AABCA1111A1Z1", "AP-DL-001"),
            ("Netmeds Wholesale", "Anita Desai", "+91 99887 00002", "wholesale@netmeds.com", "Chennai", "33AABCN2222A1Z2", "TN-DL-002"),
            ("MedPlus Distributors", "Vikram Singh", "+91 80001 00003", "dist@medplus.in", "Bengaluru", "29AABCM3333A1Z3", "KA-DL-003"),
        ]
        
        db_suppliers = []
        for s in suppliers_data:
            sup = Supplier.query.filter_by(name=s[0]).first()
            if not sup:
                sup = Supplier(name=s[0], contact=s[1], phone=s[2], email=s[3], city=s[4], gst=s[5], license=s[6])
                db.session.add(sup)
                db.session.flush()
            db_suppliers.append(sup)
            
        all_suppliers = Supplier.query.all()

        # 2. Add more medicines
        meds_data = [
            ("890100000011", "Pantoprazole 40mg", "Antacid", "Sun Pharma", random.choice(all_suppliers), 300, 120, 50, "5.00", "3.00", "12", False),
            ("890100000012", "Telmisartan 40mg", "Cardiovascular", "Cipla Ltd", random.choice(all_suppliers), 400, 180, 50, "7.50", "4.50", "12", True),
            ("890100000013", "Levocetirizine 5mg", "Antihistamine", "Dr Reddys", random.choice(all_suppliers), 250, 400, 100, "4.00", "2.00", "5", False),
            ("890100000014", "Azithromycin 500mg", "Antibiotic", "Mankind", random.choice(all_suppliers), 15, 30, 80, "20.00", "14.00", "12", True),
            ("890100000015", "Amlodipine 5mg", "Cardiovascular", "Zydus", random.choice(all_suppliers), 365, 200, 50, "3.50", "2.00", "12", True),
            ("890100000016", "Ibuprofen 400mg", "Analgesic", "Abbott", random.choice(all_suppliers), 10, 15, 50, "2.00", "1.00", "5", False), # Low stock
            ("890100000017", "Vitamin C 500mg", "Vitamins", "GSK", random.choice(all_suppliers), 500, 500, 100, "1.50", "0.80", "5", False),
            ("890100000018", "Cough Syrup 100ml", "Cold & Cough", "Dabur", random.choice(all_suppliers), 180, 45, 50, "85.00", "60.00", "12", False), # Low stock
            ("890100000019", "Insulin Glargine", "Antidiabetic", "Sanofi", random.choice(all_suppliers), 60, 25, 30, "450.00", "380.00", "12", True), # Low stock
            ("890100000020", "Thyroxine 50mcg", "Hormone", "Abbott", random.choice(all_suppliers), 200, 150, 40, "120.00", "90.00", "12", True),
            ("890100000021", "Diclofenac Gel 30g", "Analgesic", "Novartis", random.choice(all_suppliers), 300, 80, 50, "65.00", "45.00", "12", False),
            ("890100000022", "Calcium + D3", "Vitamins", "Torrent", random.choice(all_suppliers), 400, 300, 100, "8.00", "5.00", "5", False),
        ]
        
        for i, row in enumerate(meds_data, 10):
            barcode, name, category, manufacturer, supplier, days, stock, min_stock, mrp, purchase, gst, rx = row
            if not Medicine.query.filter_by(barcode=barcode).first():
                db.session.add(
                    Medicine(
                        barcode=barcode,
                        name=name,
                        category=category,
                        manufacturer=manufacturer,
                        supplier=supplier,
                        batch=f"BTH24001{i}",
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
        db.session.commit()
        
        all_meds = Medicine.query.all()

        # 3. Add more customers & prescriptions
        customer_names = ["Kiran Rao", "Amit Shah", "Priya Kulkarni", "Neha Gupta", "Ravi Kumar"]
        for cname in customer_names:
            if not Customer.query.filter_by(name=cname).first():
                cust = Customer(name=cname, phone=f"+91 98000 111{random.randint(10,99)}", age=random.randint(20, 70))
                db.session.add(cust)
                db.session.flush()
                
                # Add prescription for some
                if random.choice([True, False]):
                    db.session.add(
                        Prescription(
                            customer=cust,
                            patient_name=cname,
                            age=cust.age,
                            doctor_name=f"Dr. {random.choice(['Sharma', 'Verma', 'Iyer'])}",
                            doctor_reg_no=f"MH{random.randint(10000, 99999)}",
                            issue_date=date.today() - timedelta(days=random.randint(1, 15)),
                            valid_until=date.today() + timedelta(days=random.randint(10, 30)),
                            medicines_text=f"{random.choice(all_meds).name} - 1 tab BD",
                            status="active",
                        )
                    )
        db.session.commit()
        
        all_customers = Customer.query.all()
        all_prescriptions = Prescription.query.all()

        # 4. Add Bills and Bill Items (Historical data for charts)
        if Bill.query.count() < 20:
            for i in range(1, 26): # Create 25 bills
                bill_date = datetime.utcnow() - timedelta(days=random.randint(0, 28))
                cust = random.choice(all_customers)
                rx = random.choice(all_prescriptions) if random.choice([True, False]) else None
                
                bill = Bill(
                    invoice_number=f"INV-24-{1000 + i}",
                    customer_id=cust.id,
                    patient_name=cust.name,
                    phone=cust.phone,
                    doctor_name=rx.doctor_name if rx else "",
                    prescription_id=rx.id if rx else None,
                    bill_date=bill_date,
                    status="paid"
                )
                db.session.add(bill)
                db.session.flush()
                
                # Add 1 to 4 items
                num_items = random.randint(1, 4)
                subtotal = Decimal("0.00")
                gst_total = Decimal("0.00")
                
                for _ in range(num_items):
                    med = random.choice(all_meds)
                    qty = random.randint(1, 5)
                    line_sub = med.mrp * qty
                    line_gst = line_sub * (med.gst_rate / Decimal("100"))
                    
                    b_item = BillItem(
                        bill_id=bill.id,
                        medicine_id=med.id,
                        name=med.name,
                        batch=med.batch,
                        qty=qty,
                        mrp=med.mrp,
                        gst_rate=med.gst_rate,
                        discount=Decimal("0.00"),
                        line_total=line_sub + line_gst
                    )
                    db.session.add(b_item)
                    subtotal += line_sub
                    gst_total += line_gst
                
                bill.subtotal = subtotal
                bill.gst_total = gst_total
                bill.total = subtotal + gst_total
                
                # Add payment
                payment = Payment(
                    bill_id=bill.id,
                    mode=random.choice(["cash", "upi", "card"]),
                    amount=bill.total,
                    status="captured"
                )
                db.session.add(payment)
                
            db.session.commit()

        # 5. Add Notifications
        if Notification.query.count() < 5:
            notifications = [
                Notification(type="system", title="System Maintenance", message="Scheduled maintenance tonight at 2 AM.", severity="info"),
                Notification(type="stock", title="Low Stock Alert", message="Ibuprofen 400mg is below minimum stock level.", severity="warning"),
                Notification(type="stock", title="Expiring Soon", message="Amoxicillin 500mg batch BTH240002 is expiring in 20 days.", severity="warning"),
                Notification(type="system", title="New Feature", message="AI Assistant is now active!", severity="success"),
                Notification(type="prescription", title="Prescription Expiring", message="Prescription for Rahul Mehta is expiring soon.", severity="info"),
            ]
            db.session.add_all(notifications)
            db.session.commit()

        print("Database seeded with more realistic data successfully!")

if __name__ == "__main__":
    seed_more_data()
