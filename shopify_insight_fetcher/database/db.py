import sqlite3

conn = None

def init_db():
    global conn
    if conn is None:
        conn = sqlite3.connect("shopify_insights.db", check_same_thread=False)

# Ensure it's initialized on import
init_db()
