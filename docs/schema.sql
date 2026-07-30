-- ============================================================
-- Схема базы данных "Фото-студия" (заказ фотосессий)
-- СУБД: MySQL 8.0 (совместимо с MariaDB).
-- Для локального запуска прототипа используется SQLite —
-- см. app/database.py (тот же набор таблиц и связей).
-- ============================================================

CREATE DATABASE IF NOT EXISTS photostudio
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE photostudio;

-- ------------------------------------------------------------
-- Таблица 1. users — зарегистрированные пользователи (клиенты и администраторы)
-- ------------------------------------------------------------
CREATE TABLE users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(150)        NOT NULL,
    login           VARCHAR(50)         NOT NULL,
    password_hash   VARCHAR(255)        NOT NULL,
    phone           VARCHAR(20)         NOT NULL,
    email           VARCHAR(100)        NOT NULL,
    role            ENUM('client','admin') NOT NULL DEFAULT 'client',
    created_at      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_login UNIQUE (login),
    CONSTRAINT uq_users_email UNIQUE (email)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Таблица 2. photoshoot_types — справочник вариантов фотосессий
-- ------------------------------------------------------------
CREATE TABLE photoshoot_types (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    name              VARCHAR(100)   NOT NULL,
    description       TEXT,
    price             DECIMAL(10,2)  NOT NULL,
    duration_minutes  INT            NOT NULL
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Таблица 3. bookings — заявки клиентов на фотосессию
-- ------------------------------------------------------------
CREATE TABLE bookings (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    user_id              INT             NOT NULL,
    photoshoot_type_id   INT             NOT NULL,
    booking_date         DATE            NOT NULL,
    booking_time         TIME            NOT NULL,
    payment_method       ENUM('cash','card','online') NOT NULL,
    status               ENUM('new','confirmed','completed','cancelled') NOT NULL DEFAULT 'new',
    comment              TEXT,
    created_at           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_bookings_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_bookings_type
        FOREIGN KEY (photoshoot_type_id) REFERENCES photoshoot_types(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_bookings_user (user_id),
    INDEX idx_bookings_status (status),
    INDEX idx_bookings_date (booking_date)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Начальные данные справочника вариантов фотосессий
-- ------------------------------------------------------------
INSERT INTO photoshoot_types (name, description, price, duration_minutes) VALUES
('Портретная съёмка',   'Индивидуальная студийная фотосессия, 1 человек', 3500.00, 60),
('Семейная съёмка',     'Фотосессия для семьи до 5 человек',              6000.00, 90),
('Свадебная съёмка',    'Полный день, репортаж + постановочные кадры',    25000.00, 480),
('Предметная съёмка',   'Съёмка товаров/украшений для каталога',          2500.00, 45);

-- ------------------------------------------------------------
-- Учётная запись администратора (пароль задаётся при первом запуске
-- приложения через app/database.py -> seed_admin())
-- ------------------------------------------------------------
