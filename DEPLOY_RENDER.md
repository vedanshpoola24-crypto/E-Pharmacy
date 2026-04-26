# Deploy MedStore With Render PostgreSQL

This setup stores production data in Render PostgreSQL. The backend uses the `DATABASE_URL` environment variable; locally it can still fall back to SQLite.

## Option A: Render Blueprint

1. Push this repository to GitHub.
2. In Render, choose **New +** > **Blueprint**.
3. Select this repo. Render detects the root `render.yaml`.
4. Click **Apply**.
5. Render creates:
   - `medstore-postgres`
   - `medstore-api`
6. Wait for deploy to finish. On the free tier, migrations run as part of the start command:

```bash
flask db upgrade && flask seed && gunicorn "app:app" --config gunicorn.conf.py
```

7. Open:

```text
https://YOUR-BACKEND.onrender.com/api/health
```

You should see `{"service":"medstore-api","status":"ok"}`.

## Option B: Manual Render Setup

1. Create a **PostgreSQL** database on Render.
2. Copy its **Internal Database URL**.
3. Create a **Web Service** from this repo.
4. Set **Root Directory**:

```text
backend
```

5. Set **Build Command**:

```bash
pip install -r requirements.txt
```

6. Leave **Pre-Deploy Command** empty on the free tier.

7. Set **Start Command**:

```bash
flask db upgrade && flask seed && gunicorn "app:app" --config gunicorn.conf.py
```

8. Add environment variables:

```text
DATABASE_URL=<Render internal PostgreSQL URL>
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
4. Refresh the frontend. The record should still exist because it is stored in Render PostgreSQL.

## Import Existing SQLite Data

If you want to migrate the old `backend/medstore.db` data into Render PostgreSQL:

1. Upload or keep `medstore.db` in the backend runtime environment.
2. Open a Render Shell for `medstore-api`.
3. Run:

```bash
flask import-sqlite
```

Only do this once, or it will duplicate legacy records.
