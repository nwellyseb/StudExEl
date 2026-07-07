import sqlite3

# Connect to the database
connection = sqlite3.connect("studexel.db")
cursor = connection.cursor()

# -----------------------------
# Schools Table
# -----------------------------
# Categories Table
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name TEXT NOT NULL,
    short_name TEXT,
    school_type TEXT,
    sector TEXT,
    region TEXT,
    province TEXT,
    city TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

connection.commit()
connection.close()

print("✅ Schools table created successfully!")