from database.db import conn
import json

def save_brand_data(data):
    cursor = conn.cursor()

    # Insert into brands table
    cursor.execute("""
        INSERT INTO brands (store_name, about, contact, social)
        VALUES (?, ?, ?, ?)
    """, (
        data.get("store_name"),
        data.get("about_brand"),
        json.dumps(data.get("contact_info")),
        json.dumps(data.get("social_links"))
    ))

    brand_id = cursor.lastrowid

    # Insert products
    for product in data.get("products", []):
        cursor.execute("""
            INSERT INTO products (brand_id, title, price, url, is_hero)
            VALUES (?, ?, ?, ?, ?)
        """, (
            brand_id,
            product.get("title"),
            product.get("price"),
            product.get("url"),
            False  # these are normal products
        ))

    # Insert hero products
    for product in data.get("hero_products", []):
        cursor.execute("""
            INSERT INTO products (brand_id, title, price, url, is_hero)
            VALUES (?, ?, ?, ?, ?)
        """, (
            brand_id,
            product.get("title"),
            product.get("price"),
            product.get("url"),
            True  # hero flag
        ))

    # Insert FAQs
    for faq in data.get("faqs", []):
        cursor.execute("""
            INSERT INTO faqs (brand_id, question, answer)
            VALUES (?, ?, ?)
        """, (
            brand_id,
            faq.get("question"),
            faq.get("answer")
        ))

    # Insert policies
    cursor.execute("""
        INSERT INTO policies (brand_id, privacy_policy, refund_policy)
        VALUES (?, ?, ?)
    """, (
        brand_id,
        data.get("privacy_policy"),
        data.get("refund_policy")
    ))

    # Insert important links
    for name, url in data.get("important_links", {}).items():
        cursor.execute("""
            INSERT INTO important_links (brand_id, name, url)
            VALUES (?, ?, ?)
        """, (
            brand_id,
            name,
            url
        ))

    conn.commit()
