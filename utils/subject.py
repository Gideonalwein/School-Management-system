import sqlite3
import pandas as pd
from utils.db import get_connection

def get_all_subjects():
    """Fetch all subjects as a DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM subjects", conn)
    conn.close()
    return df

def get_subjects_as_list():
    """Return all subjects as a list of dictionaries."""
    df = get_all_subjects()
    return df.to_dict(orient="records")

def get_subject_dict():
    """Return a dictionary mapping subject ID to name."""
    df = get_all_subjects()
    return {row["id"]: row["name"] for _, row in df.iterrows()}

def get_subject_name_to_id():
    """Return a dictionary mapping subject name to ID."""
    df = get_all_subjects()
    return {row["name"]: row["id"] for _, row in df.iterrows()}

def add_subject(name):
    """Add a new subject to the database."""
    conn = get_connection()
    with conn:
        conn.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
    conn.close()

def delete_subject(subject_id):
    """Delete a subject by ID."""
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    conn.close()

def get_subject_name_by_id(subject_id):
    """Return the subject name given its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM subjects WHERE id = ?", (subject_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
