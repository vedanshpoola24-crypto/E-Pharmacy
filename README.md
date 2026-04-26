# MedStore SaaS E-Pharmacy

Production-ready Flask/PostgreSQL + static frontend implementation for an E-Pharmacy / Medical Store Management system.

## Stack

- Backend: Flask, SQLAlchemy ORM, Flask-Migrate/Alembic, JWT, Marshmallow, PostgreSQL
- Frontend: HTML, CSS, JavaScript, Chart.js, jsPDF
- Deployment: Render backend + Render PostgreSQL, Vercel/Netlify frontend

## Local Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set FLASK_APP=app.py
flask db upgrade
flask seed
flask run
```

Demo users:

- `admin@medstore.local` / `Admin@12345`
- `pharmacist@medstore.local` / `Pharma@12345`
- `cashier@medstore.local` / `Cashier@12345`

## SQLite to PostgreSQL Migration

1. Create a PostgreSQL database and set `DATABASE_URL`.
2. Run `flask db upgrade`.
3. Put the legacy `medstore.db` in `backend/`.
4. Run `flask import-sqlite`.

The new PostgreSQL schema is defined in `backend/app/models/`, the initial Alembic migration is in `backend/migrations/versions/0001_initial_schema.py`, and a SQL reference is available at `backend/postgresql_schema.sql`.

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
2. In Render, create a PostgreSQL database or use the root `render.yaml` as a Blueprint.
3. Create a Web Service:
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Pre-deploy command: `flask db upgrade && flask seed`
   - Start command: `gunicorn "app:app" --config gunicorn.conf.py`
4. Add environment variables from `backend/.env.example`.
5. Set `DATABASE_URL` from Render PostgreSQL.
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
