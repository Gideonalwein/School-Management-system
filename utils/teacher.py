import sqlite3
import pandas as pd

DB_PATH = "school.db"

import sqlite3
import pandas as pd

def get_all_teachers():
    conn = sqlite3.connect("school.db")
    query = """
    SELECT 
        id,
        first_name,
        middle_name,
        last_name,
        subject,
        hire_date,
        photo,
        phone,
        gender,
        class
    FROM teachers
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Create full_name column
    df["full_name"] = df["first_name"] + " " + df["last_name"]
    return df


def get_teacher_by_id(teacher_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teachers WHERE id = ?", (teacher_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        columns = ["id", "first_name", "middle_name", "last_name", "hire_date", "phone", "photo", "gender", "subject", "class"]
        return dict(zip(columns, row))
    return {}

def add_teacher(first_name, middle_name, last_name, hire_date, phone, photo, gender, subject, class_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO teachers (first_name, middle_name, last_name, hire_date, phone, photo, gender, subject, class)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (first_name, middle_name, last_name, hire_date, phone, photo, gender, subject, class_))
    conn.commit()
    conn.close()

def update_teacher(teacher_id, first_name, middle_name, last_name, hire_date, phone, photo, gender, subject, class_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE teachers
        SET first_name = ?, middle_name = ?, last_name = ?, hire_date = ?, phone = ?, photo = ?, gender = ?, subject = ?, class = ?
        WHERE id = ?
    """, (first_name, middle_name, last_name, hire_date, phone, photo, gender, subject, class_, teacher_id))
    conn.commit()
    conn.close()

def delete_teacher(teacher_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()
