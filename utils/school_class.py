# utils/school_class.py

import sqlite3
import pandas as pd
from .db import get_connection

def get_all_classes():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM classes")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["id", "name"])
        return df
    except Exception as e:
        print("Error fetching classes:", e)
        return pd.DataFrame()
    finally:
        conn.close()

def get_class_by_id(class_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM classes WHERE id = ?", (class_id,))
        row = cursor.fetchone()
        return {"id": row[0], "name": row[1]} if row else None
    except Exception as e:
        print("Error getting class:", e)
        return None
    finally:
        conn.close()

def add_class(name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO classes (name) VALUES (?)", (name,))
        conn.commit()
    except Exception as e:
        print("Error adding class:", e)
    finally:
        conn.close()

def delete_class(class_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
        conn.commit()
    except Exception as e:
        print("Error deleting class:", e)
    finally:
        conn.close()
