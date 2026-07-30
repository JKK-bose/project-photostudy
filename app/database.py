import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).parent / "photostudio.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT NOT NULL,
    login           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    phone           TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    role            TEXT NOT NULL DEFAULT 'client' CHECK(role IN ('client','admin')),
    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS photoshoot_types (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT NOT NULL,
    description       TEXT,
    price             DECIMAL(10,2) NOT NULL,
    duration_minutes  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id              INTEGER NOT NULL,
    photoshoot_type_id   INTEGER NOT NULL,
    booking_date         TEXT NOT NULL,
    booking_time         TEXT NOT NULL,
    payment_method       TEXT NOT NULL CHECK(payment_method IN ('cash','card','online')),
    status               TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new','confirmed','completed','cancelled')),
    comment              TEXT,
    created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (photoshoot_type_id) REFERENCES photoshoot_types(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(booking_date);
"""

PHOTOSHOOT_TYPES = [
    ("Портретная съёмка", "Индивидуальная студийная фотосессия, 1 человек", 3500.00, 60),
    ("Семейная съёмка", "Фотосессия для семьи до 5 человек", 6000.00, 90),
    ("Свадебная съёмка", "Полный день, репортаж + постановочные кадры", 25000.00, 480),
    ("Предметная съёмка", "Съёмка товаров/украшений для каталога", 2500.00, 45),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)

    cur = conn.execute("SELECT COUNT(*) AS c FROM photoshoot_types")
    if cur.fetchone()["c"] == 0:
        conn.executemany(
            "INSERT INTO photoshoot_types (name, description, price, duration_minutes) VALUES (?,?,?,?)",
            PHOTOSHOOT_TYPES,
        )

    cur = conn.execute("SELECT COUNT(*) AS c FROM users WHERE role='admin'")
    if cur.fetchone()["c"] == 0:
        conn.execute(
            "INSERT INTO users (full_name, login, password_hash, phone, email, role) VALUES (?,?,?,?,?,?)",
            (
                "Администратор студии",
                "admin",
                generate_password_hash("Admin12345"),
                "+70000000000",
                "admin@photostudio.local",
                "admin",
            ),
        )

    conn.commit()
    conn.close()
