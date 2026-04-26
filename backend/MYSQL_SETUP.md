# MySQL Setup

This backend is configured for MySQL through SQLAlchemy and Flask-Migrate.

## 1. Install MySQL

Install MySQL Server 8.x and MySQL Shell or MySQL CLI. After installation, confirm:

```powershell
mysql --version
```

## 2. Create Database And User

Login as root:

```powershell
mysql -u root -p
```

Run:

```sql
CREATE DATABASE medstore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'medstore'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON medstore.* TO 'medstore'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 3. Install Backend Dependencies

```powershell
cd "c:\pula project\E-Pharmacy\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 4. Run Migrations And Seed Data

```powershell
$env:DATABASE_URL="mysql+pymysql://medstore:password@localhost:3306/medstore"
$env:FLASK_APP="app.py"
flask db upgrade
flask seed
flask run
```

## 5. Check Tables Like MySQL Shell Screenshot

```powershell
mysql -u medstore -p medstore
```

Inside MySQL:

```sql
SHOW TABLES;
DESCRIBE medicines;
SELECT id, name, category, stock, mrp, expiry_date FROM medicines;
SELECT id, name, contact, phone, city FROM suppliers;
SELECT id, name, email, role, is_active FROM users;
```

Useful table-structure query:

```sql
SELECT
  column_name,
  column_type,
  is_nullable,
  column_key,
  column_default,
  extra
FROM information_schema.columns
WHERE table_schema = 'medstore'
  AND table_name = 'medicines'
ORDER BY ordinal_position;
```

## Schema Files

- Source of truth for the app: `app/models/__init__.py`
- Migration used to create tables: `migrations/versions/0001_initial_schema.py`
- MySQL reference SQL: `mysql_schema.sql`
