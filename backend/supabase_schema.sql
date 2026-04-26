-- PostgreSQL schema for Supabase
-- Run this in the Supabase SQL Editor

-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'pharmacist',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_users_email ON users (email);

-- Suppliers Table
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_suppliers_name ON suppliers (name);

-- Customers Table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(160) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,
    age INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_customers_name ON customers (name);
CREATE INDEX ix_customers_phone ON customers (phone);

-- Medicines Table
CREATE TABLE medicines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(180) NOT NULL,
    category VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(160),
    supplier_id INT REFERENCES suppliers(id) ON DELETE SET NULL,
    barcode VARCHAR(80) UNIQUE,
    batch VARCHAR(80),
    expiry_date DATE NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    min_stock INT NOT NULL DEFAULT 50,
    reorder_quantity INT NOT NULL DEFAULT 100,
    mrp DECIMAL(10,2) NOT NULL,
    purchase_price DECIMAL(10,2) DEFAULT 0.00,
    gst_rate DECIMAL(5,2) DEFAULT 0.00,
    rx_required BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_medicines_name ON medicines (name);
CREATE INDEX ix_medicines_category ON medicines (category);
CREATE INDEX ix_medicines_supplier_id ON medicines (supplier_id);
CREATE INDEX ix_medicines_barcode ON medicines (barcode);
CREATE INDEX ix_medicines_batch ON medicines (batch);
CREATE INDEX ix_medicines_expiry_date ON medicines (expiry_date);

-- Prescriptions Table
CREATE TABLE prescriptions (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id) ON DELETE SET NULL,
    patient_name VARCHAR(160) NOT NULL,
    age INT,
    doctor_name VARCHAR(160) NOT NULL,
    doctor_reg_no VARCHAR(80),
    issue_date DATE NOT NULL,
    valid_until DATE,
    medicines_text TEXT,
    notes TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    file_path VARCHAR(255),
    ocr_text TEXT,
    verified_by INT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_prescriptions_customer_id ON prescriptions (customer_id);
CREATE INDEX ix_prescriptions_patient_name ON prescriptions (patient_name);

-- Bills Table
CREATE TABLE bills (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(40) NOT NULL UNIQUE,
    customer_id INT REFERENCES customers(id) ON DELETE SET NULL,
    patient_name VARCHAR(160) NOT NULL,
    phone VARCHAR(50),
    doctor_name VARCHAR(160),
    prescription_id INT REFERENCES prescriptions(id) ON DELETE SET NULL,
    bill_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    gst_total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    discount_total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(30) NOT NULL DEFAULT 'paid',
    original_bill_id INT REFERENCES bills(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_bills_invoice_number ON bills (invoice_number);
CREATE INDEX ix_bills_customer_id ON bills (customer_id);
CREATE INDEX ix_bills_patient_name ON bills (patient_name);
CREATE INDEX ix_bills_bill_date ON bills (bill_date);

-- Bill Items Table
CREATE TABLE bill_items (
    id SERIAL PRIMARY KEY,
    bill_id INT NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
    medicine_id INT REFERENCES medicines(id) ON DELETE SET NULL,
    name VARCHAR(180) NOT NULL,
    batch VARCHAR(80),
    qty INT NOT NULL,
    mrp DECIMAL(10,2) NOT NULL,
    gst_rate DECIMAL(5,2) DEFAULT 0.00,
    discount DECIMAL(10,2) DEFAULT 0.00,
    line_total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_bill_items_bill_id ON bill_items (bill_id);
CREATE INDEX ix_bill_items_medicine_id ON bill_items (medicine_id);

-- Payments Table
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    bill_id INT NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
    mode VARCHAR(30) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    reference VARCHAR(120),
    status VARCHAR(30) NOT NULL DEFAULT 'captured',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_payments_bill_id ON payments (bill_id);

-- Notifications Table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    type VARCHAR(40) NOT NULL,
    title VARCHAR(180) NOT NULL,
    message TEXT NOT NULL,
    channel VARCHAR(30) NOT NULL DEFAULT 'in_app',
    recipient VARCHAR(255),
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    severity VARCHAR(20) NOT NULL DEFAULT 'info',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_notifications_type ON notifications (type);

-- Audit Logs Table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(80) NOT NULL,
    entity VARCHAR(80) NOT NULL,
    entity_id INT,
    details JSONB,
    ip_address VARCHAR(80),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_audit_logs_user_id ON audit_logs (user_id);

-- Stock Adjustments Table
CREATE TABLE stock_adjustments (
    id SERIAL PRIMARY KEY,
    medicine_id INT NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    delta INT NOT NULL,
    reason VARCHAR(160) NOT NULL,
    before_stock INT NOT NULL,
    after_stock INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_stock_adjustments_medicine_id ON stock_adjustments (medicine_id);

-- Seed Initial Admin User (password is 'admin123' hashed with Werkzeug)
-- pbkdf2:sha256:600000$c9WfBvXyP9S8$e5d7... (using a generic hash for example, user should reset)
-- Actually, let's just create the table and let the user register.
