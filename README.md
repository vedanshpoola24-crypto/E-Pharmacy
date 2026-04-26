# MedStore SaaS E-Pharmacy

Production-ready Flask/MySQL + static frontend implementation for an E-Pharmacy / Medical Store Management system.

## Stack

- Backend: Flask, SQLAlchemy ORM, Flask-Migrate/Alembic, JWT, Marshmallow, MySQL
- Frontend: HTML, CSS, JavaScript, Chart.js, jsPDF
- Deployment: Render backend + external MySQL, Vercel/Netlify frontend

## MySQL Setup

Create the database and user before running migrations:

```sql
CREATE DATABASE medstore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'medstore'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON medstore.* TO 'medstore'@'localhost';
FLUSH PRIVILEGES;
```

The backend reads the connection from `DATABASE_URL`:

```text
mysql+pymysql://medstore:password@localhost:3306/medstore
```

## Local Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=mysql+pymysql://medstore:password@localhost:3306/medstore
set FLASK_APP=app.py
flask db upgrade
flask seed
flask run
```

Demo users:

- `admin@medstore.local` / `Admin@12345`
- `pharmacist@medstore.local` / `Pharma@12345`
- `cashier@medstore.local` / `Cashier@12345`

## SQLite to MySQL Migration

1. Create a MySQL database and set `DATABASE_URL`.
2. Run `flask db upgrade`.
3. Put the legacy `medstore.db` in `backend/`.
4. Run `flask import-sqlite`.

The MySQL schema is defined in `backend/app/models/`, the initial Alembic migration is in `backend/migrations/versions/0001_initial_schema.py`, and a SQL reference is available at `backend/mysql_schema.sql`.

## Local Frontend

Open `frontend/index.html`, or serve it:

```bash
cd frontend
python -m http.server 3000
```

For deployed frontend builds, edit `frontend/js/config.js`:

```js
window.MEDSTORE_API_URL = "https://your-render-api.onrender.com";
```

## API Docs

Run the backend and open:

- Swagger UI: `http://localhost:5000/api/docs`
- OpenAPI JSON: `http://localhost:5000/openapi.json`

## Render Deployment

1. Push this repository to GitHub.
2. Create a MySQL database with a provider such as PlanetScale, Aiven, Railway, Clever Cloud, or your own server.
3. Create a Web Service:
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Pre-deploy command: leave empty on Render free tier
   - Start command: `python -m flask db upgrade && python -m flask seed && python -m gunicorn wsgi:app --config gunicorn.conf.py`
4. Add environment variables from `backend/.env.example`.
5. Set `DATABASE_URL` to your MySQL connection string.
6. Set `CORS_ORIGINS` to your Vercel/Netlify frontend URL.
7. Full cloud database instructions are in `DEPLOY_RENDER.md`.

## Frontend Deployment

Deploy the `frontend/` directory to Vercel or Netlify. Update `window.MEDSTORE_API_URL` in `index.html` or inject it during your build process.

## Tests

```bash
cd backend
pytest
```

## Included Features

Authentication, role-based access, REST APIs, validation, pagination, search, dashboard charts, GST billing, discounts, cash/card/UPI payments, PDF/print invoices, refunds, barcode lookup, batch/expiry tracking, stock adjustments, prescription upload with OCR hook, reports, notifications, AI assistant, deployment files, security headers, CORS, rate limiting, and tests.
