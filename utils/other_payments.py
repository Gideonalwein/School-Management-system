import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "school.db"

def get_all_students():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT id, first_name || ' ' || middle_name || ' ' || last_name AS full_name FROM students", conn)

def get_other_payments():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("""
            SELECT 
                op.id, 
                s.first_name || ' ' || s.middle_name || ' ' || s.last_name AS student_name,
                op.student_id,
                op.category,
                op.amount_paid,
                op.payment_date,
                op.term,
                op.year,
                op.method,
                op.description,
                op.receipt,
                op.receipt_type
            FROM other_payments op
            JOIN students s ON s.id = op.student_id
            ORDER BY op.payment_date DESC
        """, conn)

def add_other_payment(student_id, category, amount_paid, payment_date, term, year, method, description, receipt=None, receipt_type=None):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO other_payments 
                (student_id, category, amount_paid, payment_date, term, year, method, description, receipt, receipt_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, category, amount_paid, payment_date, term, year, method, description, receipt, receipt_type))
        conn.commit()

def update_other_payment(record_id, student_id, category, amount_paid, payment_date, term, year, method, description, receipt=None, receipt_type=None):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        if receipt is not None:
            c.execute("""
                UPDATE other_payments SET 
                    student_id=?, category=?, amount_paid=?, payment_date=?,
                    term=?, year=?, method=?, description=?,
                    receipt=?, receipt_type=?
                WHERE id=?
            """, (student_id, category, amount_paid, payment_date, term, year, method, description, receipt, receipt_type, record_id))
        else:
            c.execute("""
                UPDATE other_payments SET 
                    student_id=?, category=?, amount_paid=?, payment_date=?,
                    term=?, year=?, method=?, description=?
                WHERE id=?
            """, (student_id, category, amount_paid, payment_date, term, year, method, description, record_id))
        conn.commit()

def delete_other_payment(record_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM other_payments WHERE id=?", (record_id,))
        conn.commit()

def get_payment_summary():
    df = get_other_payments()
    summary = df.groupby('category')["amount_paid"].sum().reset_index().sort_values(by="amount_paid", ascending=False)
    return summary

def export_payments_to_csv(file_path="other_payments_export.csv"):
    df = get_other_payments()
    df.to_csv(file_path, index=False)
    return file_path

def get_receipt_blob_by_id(record_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT receipt, receipt_type FROM other_payments WHERE id=?", (record_id,))
        return c.fetchone()
    
def get_student_names_map():
    """Returns a dictionary of student_id → full name (for display in filters/search)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, first_name || ' ' || last_name FROM students")
    result = dict(c.fetchall())
    conn.close()
    return result

def get_all_other_payments():
    """Fetch all other payments and join with student name."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            op.id,
            s.first_name || ' ' || IFNULL(s.middle_name || ' ', '') || s.last_name AS student_name,
            op.student_id,
            op.category,
            op.amount_paid,
            op.payment_date,
            op.term,
            op.year,
            op.method,
            op.description,
            op.receipt,
            op.receipt_type
        FROM other_payments op
        JOIN students s ON op.student_id = s.id
        ORDER BY op.payment_date DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df