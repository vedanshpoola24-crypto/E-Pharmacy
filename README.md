
           _      _  _____ _                      
          | |    | |/ ____| |                     
 _ __ ___ | |  __| | (___ | |_ ___  _ __ ___     
| '_ ` _ \| | / _` |\___ \| __/ _ \| '__/ _ \    
| | | | | | || (_| |____) | || (_) | | |  __/    
|_| |_| |_|_| \__,_|_____/ \__\___/|_|  \___|    
                                                  
      ++ SUPABASE POWERED E-PHARMACY ++

# 💊 MedStore SaaS: The Ultimate E-Pharmacy Engine 🚀

Welcome to the **MedStore SaaS**, a high-performance, production-ready pharmacy management system engineered for speed, security, and scalability. Now supercharged with **Supabase PostgreSQL** and **AI-Driven Analytics**.

## 🔥 What's New? (The "Crazy" Migration)
We just ripped out the old MySQL engine and replaced it with a **Twin-Turbo Supabase PostgreSQL** backend. 
- **Zero Latency**: Direct PostgreSQL connections with SSL.
- **Auto-Healing**: SQL Engine with `pool_pre_ping` and `pool_recycle`.
- **Bulletproof Schema**: Optimized PostgreSQL types for precision billing.
- **Streamlined UI**: Removed redundant fields (Address/License) to make data entry lightning fast!

## 🛠️ The Tech Stack of Champions
- **Backend**: Python Flask 🐍 + SQLAlchemy 🛡️ + JWT Auth 🔑
- **Database**: Supabase PostgreSQL ⚡ (The Cloud King)
- **Frontend**: Ultra-light Vanilla JS ⚡ + Chart.js 📊 + Lucide Icons ✨
- **Security**: Flask-Limiter + CORS + Secure Headers 🔒
- **Intelligence**: AI-Assistant for Inventory + Prescription OCR 🤖

## ⚡ Quick Start (Locally)

### 1. The Brain (Backend)
```bash
cd backend
# Create & Activate Venv
python -m venv venv
.\venv\Scripts\activate

# Install the Arsenal
pip install -r requirements.txt

# Run the Engine
$env:FLASK_APP="wsgi.py"
flask run
```

### 2. The Face (Frontend)
```bash
cd frontend
# Serve it like a Pro
python -m http.server 5500
```
Visit: `http://localhost:5500`

## 🌍 Environment Secrets (`.env`)
Your `.env` file is your control room. Configure it like this:
```text
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres?sslmode=require
SECRET_KEY=YourSuperSecretKey
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

## 🚀 Features That Will Blow Your Mind
- **📦 Smart Inventory**: Barcode scanning + Batch tracking + Expiry alerts.
- **💰 Precision Billing**: GST calculation + Multiple payment modes (UPI/Card/Cash).
- **📄 Prescription OCR**: Upload prescriptions and let the AI extract the data.
- **📊 Real-time Dashboard**: Track sales trends and profit/loss in real-time.
- **🤖 AI Pharmacist**: A built-in assistant that knows your stock better than you do!

---
**MedStore SaaS** - *Because your pharmacy deserves a Ferrari, not a Bullock Cart.* 🏎️💨
