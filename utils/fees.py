import sqlite3
import pandas as pd
from datetime import datetime

DB = "school.db"

def create_connection():
    return sqlite3.connect(DB, check_same_thread=False)

def get_fee_structures():
    conn = create_connection()
    query = '''
        SELECT id, level, amount, year, term 
        FROM fee_structures 
        ORDER BY year DESC, term
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def add_fee_structure(level, amount, year, term):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fee_structures (level, amount, year, term)
        VALUES (?, ?, ?, ?)
    ''', (level, amount, year, term))
    conn.commit()
    conn.close()

def delete_fee_structure(structure_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fee_structures WHERE id = ?", (structure_id,))
    conn.commit()
    conn.close()

def get_fee_payments(class_level=None):
    conn = create_connection()
    query = '''
        SELECT 
            p.id, 
            s.first_name || ' ' || s.middle_name || ' ' || s.last_name AS student_name,
            c.name AS class_level,
            p.amount_paid, 
            p.payment_date, 
            p.method, 
            p.term, 
            p.year
        FROM fee_payments p
        JOIN students s ON p.student_id = s.id
        LEFT JOIN classes c ON s.class_id = c.id
    '''
    if class_level:
        query += " WHERE c.name = ?"
        df = pd.read_sql_query(query, conn, params=(class_level,))
    else:
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def add_fee_payment(student_id, amount_paid, payment_date, method, term, year):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fee_payments (student_id, amount_paid, payment_date, method, term, year)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_id, amount_paid, payment_date, method, term, year))
    conn.commit()
    conn.close()

def delete_fee_payment(payment_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fee_payments WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()

def get_student_fee_summary():
    conn = create_connection()
    query = '''
        SELECT 
            s.id AS student_id,
            s.first_name || ' ' || s.middle_name || ' ' || s.last_name AS student_name,
            c.name AS class_level,
            fs.amount AS expected_fee,
            fp.amount_paid,
            fp.term,
            fp.year
        FROM students s
        LEFT JOIN classes c ON s.class_id = c.id
        LEFT JOIN fee_payments fp ON s.id = fp.student_id
        LEFT JOIN fee_structures fs 
            ON fs.level = c.name AND fs.term = fp.term AND fs.year = fp.year
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return df

    # Fill NA values
    df['expected_fee'] = df['expected_fee'].fillna(0)
    df['amount_paid'] = df['amount_paid'].fillna(0)

    # Group by student, class, term, and year
    grouped = df.groupby(
        ["student_id", "student_name", "class_level", "term", "year"],
        as_index=False
    ).agg({
        "expected_fee": "max",   # fee per term should be consistent
        "amount_paid": "sum"
    })

    grouped["balance"] = grouped["expected_fee"] - grouped["amount_paid"]
    return grouped


def get_fee_summary(class_level=None):
    conn = create_connection()
    query = '''
        SELECT 
            c.name AS class_level,
            COUNT(DISTINCT s.id) AS num_students,
            COALESCE(SUM(fs.amount), 0) AS total_expected,
            COALESCE(SUM(fp.amount_paid), 0) AS total_paid,
            COALESCE(SUM(fs.amount), 0) - COALESCE(SUM(fp.amount_paid), 0) AS total_balance
        FROM students s
        LEFT JOIN classes c ON s.class_id = c.id
        LEFT JOIN fee_structures fs ON fs.level = c.name
        LEFT JOIN fee_payments fp 
            ON s.id = fp.student_id AND fs.term = fp.term AND fs.year = fp.year
    '''
    params = ()
    if class_level:
        query += " WHERE c.name = ?"
        params = (class_level,)

    query += " GROUP BY c.name ORDER BY c.name"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df
