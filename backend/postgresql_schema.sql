-- PostgreSQL schema reference. The executable source of truth is the Alembic
-- migration in migrations/versions/0001_initial_schema.py.

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(30) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE suppliers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(180) NOT NULL,
  contact VARCHAR(120) NOT NULL,
  phone VARCHAR(50) NOT NULL,
  email VARCHAR(255),
  address TEXT,
  city VARCHAR(120),
  gst VARCHAR(30),
  license VARCHAR(80),
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(160) NOT NULL,
  phone VARCHAR(50),
  email VARCHAR(255),
  address TEXT,
  age INTEGER,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE medicines (
  id SERIAL PRIMARY KEY,
  name VARCHAR(180) NOT NULL,
  category VARCHAR(100) NOT NULL,
  manufacturer VARCHAR(160),
  supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
  barcode VARCHAR(80) UNIQUE,
  batch VARCHAR(80),
  expiry_date DATE NOT NULL,
  stock INTEGER NOT NULL,
  min_stock INTEGER NOT NULL,
  reorder_quantity INTEGER NOT NULL,
  mrp NUMERIC(10,2) NOT NULL,
  purchase_price NUMERIC(10,2),
  gst_rate NUMERIC(5,2),
  rx_required BOOLEAN NOT NULL DEFAULT FALSE,
  description TEXT,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE prescriptions (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
  patient_name VARCHAR(160) NOT NULL,
  age INTEGER,
  doctor_name VARCHAR(160) NOT NULL,
  doctor_reg_no VARCHAR(80),
  issue_date DATE NOT NULL,
  valid_until DATE,
  medicines_text TEXT,
  notes TEXT,
  status VARCHAR(30) NOT NULL,
  file_path VARCHAR(255),
  ocr_text TEXT,
  verified_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE bills (
  id SERIAL PRIMARY KEY,
  invoice_number VARCHAR(40) NOT NULL UNIQUE,
  customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
  patient_name VARCHAR(160) NOT NULL,
  phone VARCHAR(50),
  doctor_name VARCHAR(160),
  prescription_id INTEGER REFERENCES prescriptions(id) ON DELETE SET NULL,
  bill_date TIMESTAMP NOT NULL,
  subtotal NUMERIC(10,2) NOT NULL,
  gst_total NUMERIC(10,2) NOT NULL,
  discount_total NUMERIC(10,2) NOT NULL,
  total NUMERIC(10,2) NOT NULL,
  status VARCHAR(30) NOT NULL,
  original_bill_id INTEGER REFERENCES bills(id) ON DELETE SET NULL,
  notes TEXT,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE bill_items (
  id SERIAL PRIMARY KEY,
  bill_id INTEGER NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
  medicine_id INTEGER REFERENCES medicines(id) ON DELETE SET NULL,
  name VARCHAR(180) NOT NULL,
  batch VARCHAR(80),
  qty INTEGER NOT NULL,
  mrp NUMERIC(10,2) NOT NULL,
  gst_rate NUMERIC(5,2),
  discount NUMERIC(10,2),
  line_total NUMERIC(10,2) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE payments (
  id SERIAL PRIMARY KEY,
  bill_id INTEGER NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
  mode VARCHAR(30) NOT NULL,
  amount NUMERIC(10,2) NOT NULL,
  reference VARCHAR(120),
  status VARCHAR(30) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE notifications (
  id SERIAL PRIMARY KEY,
  type VARCHAR(40) NOT NULL,
  title VARCHAR(180) NOT NULL,
  message TEXT NOT NULL,
  channel VARCHAR(30) NOT NULL,
  recipient VARCHAR(255),
  is_read BOOLEAN NOT NULL DEFAULT FALSE,
  severity VARCHAR(20) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
  action VARCHAR(80) NOT NULL,
  entity VARCHAR(80) NOT NULL,
  entity_id INTEGER,
  details JSONB,
  ip_address VARCHAR(80),
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE stock_adjustments (
  id SERIAL PRIMARY KEY,
  medicine_id INTEGER NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
  user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
  delta INTEGER NOT NULL,
  reason VARCHAR(160) NOT NULL,
  before_stock INTEGER NOT NULL,
  after_stock INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
