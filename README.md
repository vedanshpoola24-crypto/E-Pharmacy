```
███╗   ███╗███████╗██████╗ ███████╗████████╗ ██████╗ ██████╗ ███████╗
████╗ ████║██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝
██╔████╔██║█████╗  ██║  ██║███████╗   ██║   ██║   ██║██████╔╝█████╗  
██║╚██╔╝██║██╔══╝  ██║  ██║╚════██║   ██║   ██║   ██║██╔══██╗██╔══╝  
██║ ╚═╝ ██║███████╗██████╔╝███████║   ██║   ╚██████╔╝██║  ██║███████╗
╚═╝     ╚═╝╚══════╝╚═════╝ ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝

         💊  E-PHARMACY MANAGEMENT SYSTEM  💊
     "Because managing medicine shouldn't make you sick."
```

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)
![PostgreSQL](https://img.shields.io/badge/Supabase_PostgreSQL-Ready-3ECF8E?style=for-the-badge&logo=supabase)
![JWT](https://img.shields.io/badge/JWT-Secured-orange?style=for-the-badge&logo=jsonwebtokens)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## ⚡ What the heck IS this?

**MedStore SaaS** is a full-stack, production-grade, cloud-powered pharmacy management system that makes running a medical store feel like flying a fighter jet. No more Excel sheets. No more sticky notes. No more "bhai stock hai kya?" panic moments.

We're talking:
- 🛡️ **JWT Auth** — Only real pharmacists get in.
- 💊 **Smart Inventory** — Know your stock before your stock knows it's low.
- 🧾 **GST Billing Engine** — Invoices with real math, not calculator vibes.
- 🤖 **AI Assistant** — Your 24/7 digital pharmacist powered by **Groq (Llama 3.3)**.
- 📸 **Prescription OCR** — Upload an image, get the medicines extracted. Automagically.
- 🌩️ **Supabase PostgreSQL** — Cloud-native database on steroids.

---

## 🔥 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│   Vanilla JS   ·   Chart.js   ·   jsPDF   ·   Lucide   │
│              http://localhost:5500                       │
└──────────────────────────┬──────────────────────────────┘
                           │  REST API (JSON)
                           ▼
┌─────────────────────────────────────────────────────────┐
│                       BACKEND                           │
│    Flask  ·  SQLAlchemy  ·  Marshmallow  ·  JWT Auth    │
│                  http://localhost:5000                   │
└──────────────────────────┬──────────────────────────────┘
                           │  PostgreSQL Wire Protocol
                           │  SSL Encrypted ✅
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   SUPABASE CLOUD DB                     │
│         PostgreSQL  ·  12 Tables  ·  Auto-SERIAL        │
│         pool_pre_ping ✅  pool_recycle=300s ✅           │
└─────────────────────────────────────────────────────────┘
```

---

## 🗃️ Database Schema (12 Tables of Glory)

| Table | What it does |
|-------|-------------|
| `users` | Auth, roles (admin/pharmacist/cashier) |
| `medicines` | Inventory with batch, expiry, barcode |
| `suppliers` | Vendor management |
| `customers` | Patient records |
| `prescriptions` | Rx uploads with OCR hook |
| `bills` | Invoice generation with GST |
| `bill_items` | Line items per invoice |
| `payments` | Cash / Card / UPI tracking |
| `notifications` | Low stock & expiry alerts |
| `audit_logs` | Every action, tracked forever |
| `stock_adjustments` | Stock in/out ledger |
| `alembic_version` | Migration state (don't touch) |

---

## 🚀 Quick Start (Zero to Hero in 5 Steps)

### Step 1 — Clone the beast
```bash
git clone https://github.com/vedanshpoola24-crypto/E-Pharmacy.git
cd E-Pharmacy
```

### Step 2 — Build the venv fortress
```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux
```

### Step 3 — Install the Arsenal
```bash
cd backend
pip install -r requirements.txt
```

### Step 4 — Configure your `.env`
```bash
# backend/.env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres?sslmode=require
SECRET_KEY=make-this-super-random-or-get-hacked
JWT_SECRET_KEY=another-very-secret-key
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
GROQ_API_KEY=your-groq-api-key-here
```

### Step 5 — LAUNCH 🚀
```bash
# Terminal 1 — Backend
$env:FLASK_APP="wsgi.py"  # PowerShell
flask run

# Terminal 2 — Frontend
cd frontend
python -m http.server 5500
```

Open **http://localhost:5500** and witness glory.

---
## 🔑 Default Demo Credentials

| Role | Email | Password |
|------|-------|---------|
| 👑 Admin | `admin@medstore.local` | `Admin@12345` |
| 💊 Pharmacist | `pharmacist@medstore.local` | `Pharma@12345` |
| 💸 Cashier | `cashier@medstore.local` | `Cashier@12345` |

> ⚠️ **Change these if you deploy. Seriously.**

---

## 🛣️ API Endpoints (The Full Map)

```
POST   /api/auth/register       → Create user
POST   /api/auth/login          → Get JWT token

GET    /api/medicines           → List inventory
POST   /api/medicines           → Add medicine
PUT    /api/medicines/<id>      → Update medicine
DELETE /api/medicines/<id>      → Remove medicine
POST   /api/medicines/<id>/adjust → Stock adjustment

GET    /api/suppliers           → List suppliers
POST   /api/suppliers           → Add supplier

GET    /api/bills               → List invoices
POST   /api/bills               → Create invoice (GST billing)
POST   /api/bills/<id>/refund   → Refund invoice

GET    /api/prescriptions       → List prescriptions
POST   /api/prescriptions       → Upload prescription + OCR

GET    /api/dashboard/stats     → Dashboard metrics
GET    /api/dashboard/expiring  → Expiry alerts
GET    /api/notifications       → System notifications

POST   /api/chat                → AI Assistant

GET    /api/health              → Health check (DB ping)
```

---

## 🧰 Tech Stack (The Avengers Lineup)

| Component | Technology |
|-----------|-----------|
| 🐍 Language | Python 3.11+ |
| 🌶️ Framework | Flask 3.0 |
| 🗄️ ORM | SQLAlchemy 2.0 |
| ☁️ Database | Supabase PostgreSQL |
| 🔐 Auth | Flask-JWT-Extended |
| 📦 Migrations | Flask-Migrate (Alembic) |
| ✅ Validation | Marshmallow |
<<<<<<< HEAD
=======
| 🧠 AI Engine | Groq API (Llama-3.3-70b-versatile) |
>>>>>>> 78b8890 (added ai assistant and improved frontend)
| 🛡️ Rate Limiting | Flask-Limiter |
| 🌐 CORS | Flask-Cors |
| 📊 Charts | Chart.js |
| 📄 PDF | jsPDF |
| 🎨 Icons | Lucide |
| 🖥️ Server | Gunicorn (production) |

---

## 🔒 Security Features

- **JWT-based authentication** — Stateless, expiry-aware tokens
- **Role-based access control** — Admin > Pharmacist > Cashier
- **Rate limiting** — Brute force protection
- **CORS whitelist** — Only approved origins get through
- **Security headers** — X-Frame-Options, HSTS, CSP hints
- **Input sanitization** — All inputs cleaned before DB write
- **Audit log** — Every mutation tracked with user + IP
- **SSL database connection** — `sslmode=require` enforced

---

## 💥 The Migration Story (MySQL → Supabase)

This project was born on MySQL. Then we grew up.

```
MySQL + PyMySQL        →   PostgreSQL + psycopg2-binary
AUTO_INCREMENT         →   SERIAL (BIGSERIAL)
mysql+pymysql://...    →   postgresql://...?sslmode=require
Old Alembic migrations →   Fresh Postgres-native migrations
Hardcoded db config    →   python-dotenv .env loading
pool_pre_ping: ❌      →   pool_pre_ping: ✅
pool_recycle: ❌       →   pool_recycle=300: ✅
```

---

## 📁 Project Structure

```
E-Pharmacy/
├── backend/
│   ├── app/
│   │   ├── models/         # SQLAlchemy models (12 tables)
│   │   ├── routes/         # API blueprints (auth, bills, etc.)
│   │   ├── schemas/        # Marshmallow validation
│   │   ├── services/       # Business logic (billing engine)
│   │   └── utils/          # Helpers (pagination, security)
│   ├── migrations/         # Alembic migrations (PostgreSQL)
│   ├── supabase_schema.sql # Raw SQL schema for Supabase
│   ├── requirements.txt    # Python dependencies
│   ├── wsgi.py             # WSGI entry point
│   └── .env                # 🔒 YOUR SECRETS (never commit!)
├── frontend/
│   ├── js/
│   │   ├── config.js       # API URL switcher (local/prod)
│   │   └── app.js          # Entire SPA logic (one file, no BS)
│   ├── css/styles.css      # All the styles
│   └── index.html          # The face of the app
├── .gitignore              # Keeps secrets secret
└── README.md               # You're reading this masterpiece
```

---

## 🎯 Features At A Glance

```
✅ User Registration & Login (JWT)
✅ Role-Based Access (Admin / Pharmacist / Cashier)
✅ Medicine Inventory (CRUD + Barcode Lookup)
✅ Batch & Expiry Date Tracking
✅ Low Stock Alerts & Notifications
✅ Supplier Management
✅ Patient & Customer Records
✅ GST-Compliant Invoice Generation
✅ Multi-Mode Payments (Cash / Card / UPI)
✅ Invoice Refunds
✅ Prescription Upload with OCR Hook
✅ Real-Time Dashboard (Charts, Metrics)
✅ Sales Trend Analytics
✅ Profit / Loss Reports
✅ GST Report
✅ Supplier-wise Inventory Reports
✅ Stock Adjustment Ledger
<<<<<<< HEAD
✅ AI Chatbot Assistant
=======
✅ AI Chatbot Assistant (Groq Llama 3.3 + Spline 3D Model)
>>>>>>> 78b8890 (added ai assistant and improved frontend)
✅ PDF Invoice Export
✅ Audit Logs (every action tracked)
✅ Dark / Light Theme Toggle
✅ Fully Responsive UI
✅ Supabase Cloud PostgreSQL
✅ Production-grade Connection Pooling
✅ SSL-Encrypted DB Connection
```

---

## 🤝 Contributing

Found a bug? Have a feature idea? Open a PR or raise an issue.  
Fork → Branch → Code → PR → Merge → 🎉

---

## 📜 License

MIT License. Do whatever you want. Just don't sell expired medicines.

---

<div align="center">

**Built with 💊 caffeine, 🩺 obsession, and zero tolerance for bad pharmacy software.**

*MedStore SaaS — Your pharmacy, supercharged.*

</div>
