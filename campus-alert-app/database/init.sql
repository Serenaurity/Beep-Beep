-- Campus Alert Database Schema

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    detail TEXT,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    reporter VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);
CREATE INDEX idx_messages_created ON messages(created_at DESC);

INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@thammasat.ac.th', 'hashed_password_here', 'admin'),
('student1', 'student1@thammasat.ac.th', 'hashed_password_here', 'user');

INSERT INTO alerts (type, title, detail, latitude, longitude, reporter, status) VALUES
('suspicious', 'พบบุคคลน่าสงสัย', 'พบชายสวมหมวกดำ วนเวียนบริเวณอาคาร 3', 13.8659, 100.4933, 'นักศึกษา A', 'active'),
('tree', 'ต้นไม้ล้ม', 'ต้นไม้ใหญ่ล้มขวางถนนหน้าคณะวิศวะ', 13.8668, 100.4925, 'นักศึกษา B', 'active'),
('flood', 'น้ำท่วมขัง', 'น้ำท่วมสูงประมาณ 20 ซม. บริเวณลานจอดรถ', 13.8658, 100.4912, 'นักศึกษา C', 'active');

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE
ON alerts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
