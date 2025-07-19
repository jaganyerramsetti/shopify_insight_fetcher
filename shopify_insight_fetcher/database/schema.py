from database.db import conn

def create_tables():
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_name TEXT,
            about TEXT,
            contact TEXT,
            social TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id INTEGER,
            title TEXT,
            price REAL,
            url TEXT,
            is_hero BOOLEAN,
            FOREIGN KEY(brand_id) REFERENCES brands(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id INTEGER,
            question TEXT,
            answer TEXT,
            FOREIGN KEY(brand_id) REFERENCES brands(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id INTEGER,
            privacy_policy TEXT,
            refund_policy TEXT,
            FOREIGN KEY(brand_id) REFERENCES brands(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS important_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id INTEGER,
            name TEXT,
            url TEXT,
            FOREIGN KEY(brand_id) REFERENCES brands(id)
        )
    """)

    conn.commit()
