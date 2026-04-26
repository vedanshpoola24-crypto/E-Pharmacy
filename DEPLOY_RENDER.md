# Deploy MedStore With MySQL

This setup stores production data in MySQL. The backend uses the `DATABASE_URL` environment variable.

## Option A: Render Web Service

1. Push this repository to GitHub.
2. Create a MySQL database with a provider such as PlanetScale, Aiven, Railway, Clever Cloud, or your own server.
3. Copy the MySQL connection string in SQLAlchemy format:

```text
mysql+pymysql://USER:PASSWORD@HOST:3306/DATABASE
```

4. In Render, choose **New +** > **Web Service**.
5. Select this repo and set **Root Directory** to `backend`.
6. Set the build command to `pip install -r requirements.txt`.
7. Set the start command:

```bash
python -m flask db upgrade && python -m flask seed && python -m gunicorn wsgi:app --config gunicorn.conf.py
```

8. Add `DATABASE_URL` and the other environment variables from `backend/.env.example`.
9. Open:

```text
https://YOUR-BACKEND.onrender.com/api/health
```

You should see `{"service":"medstore-api","status":"ok"}`.

## Manual Render Settings

Set **Root Directory**:

```text
backend
```

Set **Build Command**:

```bash
pip install -r requirements.txt
```

Leave **Pre-Deploy Command** empty on the free tier.

Set **Start Command**:

```bash
python -m flask db upgrade && python -m flask seed && python -m gunicorn wsgi:app --config gunicorn.conf.py
```

Add environment variables:

```text
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:3306/DATABASE
SECRET_KEY=<long random secret>
JWT_SECRET_KEY=<long random secret>
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.netlify.app,http://localhost:3000
JWT_EXPIRES_HOURS=12
WEB_CONCURRENCY=2
```

## Connect The Frontend

In `frontend/js/config.js`, set your Render backend URL:

```js
window.MEDSTORE_API_URL = "https://YOUR-BACKEND.onrender.com";
```

Then deploy `frontend/` to Vercel or Netlify.

## Verify Cloud Data

1. Login using the seeded admin:

```text
admin@medstore.local
Admin@12345
```

2. Add a medicine or supplier in the frontend.
3. Restart/redeploy the Render backend.
4. Refresh the frontend. The record should still exist because it is stored in MySQL.

## Import Existing SQLite Data

If you want to migrate the old `backend/medstore.db` data into MySQL:

1. Upload or keep `medstore.db` in the backend runtime environment.
2. Open a Render Shell for `medstore-api`.
3. Run:

```bash
flask import-sqlite
```

Only do this once, or it will duplicate legacy records.
