import sqlite3
import pandas as pd

DB_PATH = "school.db"

def get_all_classes():
    """Return a DataFrame of all classes."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, name FROM classes", conn)
    conn.close()
    return df


def get_class_name_by_id(class_id):
    """Return class name for a given class ID."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM classes WHERE id = ?", (class_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else None


def add_class(name):
    """Add a new class."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO classes (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def update_class(class_id, name):
    """Update an existing class."""
    conn = sqlite3.connect(DB_PATH)
    cur
