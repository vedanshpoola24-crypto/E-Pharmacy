-- MySQL schema reference. The executable source of truth is the Alembic
-- migration in migrations/versions/0001_initial_schema.py.

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(30) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  INDEX ix_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE suppliers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(180) NOT NULL,
  contact VARCHAR(120) NOT NULL,
  phone VARCHAR(50) NOT NULL,
  email VARCHAR(255),
  address TEXT,
  city VARCHAR(120),
  gst VARCHAR(30),
  license VARCHAR(80),
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  INDEX ix_suppliers_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE customers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(160) NOT NULL,
  phone VARCHAR(50),
  email VARCHAR(255),
  address TEXT,
  age INT,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  INDEX ix_customers_name (name),
  INDEX ix_customers_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE medicines (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(180) NOT NULL,
  category VARCHAR(100) NOT NULL,
  manufacturer VARCHAR(160),
  supplier_id INT,
  barcode VARCHAR(80) UNIQUE,
  batch VARCHAR(80),
  expiry_date DATE NOT NULL,
  stock INT NOT NULL,
  min_stock INT NOT NULL,
  reorder_quantity INT NOT NULL,
  mrp DECIMAL(10,2) NOT NULL,
  purchase_price DECIMAL(10,2),
  gst_rate DECIMAL(5,2),
  rx_required BOOLEAN NOT NULL DEFAULT FALSE,
  description TEXT,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  CONSTRAINT fk_medicines_supplier_id FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
  INDEX ix_medicines_name (name),
  INDEX ix_medicines_category (category),
  INDEX ix_medicines_supplier_id (supplier_id),
  INDEX ix_medicines_barcode (barcode),
  INDEX ix_medicines_batch (batch),
  INDEX ix_medicines_expiry_date (expiry_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE prescriptions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT,
  patient_name VARCHAR(160) NOT NULL,
  age INT,
  doctor_name VARCHAR(160) NOT NULL,
  doctor_reg_no VARCHAR(80),
  issue_date DATE NOT NULL,
  valid_until DATE,
  medicines_text TEXT,
  notes TEXT,
  status VARCHAR(30) NOT NULL,
  file_path VARCHAR(255),
  ocr_text TEXT,
  verified_by INT,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  CONSTRAINT fk_prescriptions_customer_id FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
  CONSTRAINT fk_prescriptions_verified_by FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
  INDEX ix_prescriptions_customer_id (customer_id),
  INDEX ix_prescriptions_patient_name (patient_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE bills (
  id INT AUTO_INCREMENT PRIMARY KEY,
  invoice_number VARCHAR(40) NOT NULL UNIQUE,
  customer_id INT,
  patient_name VARCHAR(160) NOT NULL,
  phone VARCHAR(50),
  doctor_name VARCHAR(160),
  prescription_id INT,
  bill_date DATETIME NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  gst_total DECIMAL(10,2) NOT NULL,
  discount_total DECIMAL(10,2) NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  status VARCHAR(30) NOT NULL,
  original_bill_id INT,
  notes TEXT,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  CONSTRAINT fk_bills_customer_id FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
  CONSTRAINT fk_bills_prescription_id FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE SET NULL,
  CONSTRAINT fk_bills_original_bill_id FOREIGN KEY (original_bill_id) REFERENCES bills(id) ON DELETE SET NULL,
  INDEX ix_bills_invoice_number (invoice_number),
  INDEX ix_bills_customer_id (customer_id),
  INDEX ix_bills_patient_name (patient_name),
  INDEX ix_bills_bill_date (bill_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE bill_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  bill_id INT NOT NULL,
  medicine_id INT,
  name VARCHAR(180) NOT NULL,
  batch VARCHAR(80),
  qty INT NOT NULL,
  mrp DECIMAL(10,2) NOT NULL,
  gst_rate DECIMAL(5,2),
  discount DECIMAL(10,2),
  line_total DECIMAL(10,2) NOT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  CONSTRAINT fk_bill_items_bill_id FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
  CONSTRAINT fk_bill_items_medicine_id FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE SET NULL,
  INDEX ix_bill_items_bill_id (bill_id),
  INDEX ix_bill_items_medicine_id (medicine_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE payments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  bill_id INT NOT NULL,
  mode VARCHAR(30) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  reference VARCHAR(120),
  status VARCHAR(30) NOT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  CONSTRAINT fk_payments_bill_id FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
  INDEX ix_payments_bill_id (bill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  type VARCHAR(40) NOT NULL,
  title VARCHAR(180) NOT NULL,
  message TEXT NOT NULL,
  channel VARCHAR(30) NOT NULL,
  recipient VARCHAR(255),
  is_read BOOLEAN NOT NULL DEFAULT FALSE,
  severity VARCHAR(20) NOT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  INDEX ix_notifications_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE audit_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  action VARCHAR(80) NOT NULL,
  entity VARCHAR(80) NOT NULL,
  entity_id INT,
  details JSON,
  ip_address VARCHAR(80),
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  CONSTRAINT fk_audit_logs_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  INDEX ix_audit_logs_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE stock_adjustments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  medicine_id INT NOT NULL,
  user_id INT,
  delta INT NOT NULL,
  reason VARCHAR(160) NOT NULL,
  before_stock INT NOT NULL,
  after_stock INT NOT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  CONSTRAINT fk_stock_adjustments_medicine_id FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE,
  CONSTRAINT fk_stock_adjustments_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  INDEX ix_stock_adjustments_medicine_id (medicine_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
