import sqlite3
import os

DB_NAME = "office.db"

if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print("🗑 Eski DB silindi")

db = sqlite3.connect(DB_NAME)
db.execute("PRAGMA foreign_keys = ON;")
cur = db.cursor()

# USERS
cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    room TEXT
)
""")

# PRODUCTS
cur.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image TEXT,
    has_options INTEGER DEFAULT 0
)
""")

# PRODUCT OPTIONS
cur.execute("""
CREATE TABLE product_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
)
""")

# ORDERS  ✅ ODA EKLİ
cur.execute("""
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    option TEXT,
    qty INTEGER DEFAULT 1,
    room TEXT,
    status TEXT DEFAULT 'bekliyor',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# ADMIN
cur.execute("""
INSERT INTO users (username,password,role,room)
VALUES ('admin','123','admin','Yönetim')
""")

# CAFE (MUTFAK) KULLANICISI
cur.execute("""
INSERT INTO users (username,password,role)
VALUES ('kafe','123','cafe')
""")

db.commit()
db.close()

print("✅ DB hazır")
print("admin / 123")
print("kafe / 123")
