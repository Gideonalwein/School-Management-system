import sqlite3
from datetime import datetime
import pandas as pd

DB_NAME = "school.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def generate_admission_number():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    new_adm_number = f"ADM{count + 1:03d}"
    conn.close()
    return new_adm_number


def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT students.id, students.admission_number, students.first_name, students.middle_name,
               students.last_name, students.dob, students.gender, classes.name AS class
        FROM students
        LEFT JOIN classes ON students.class_id = classes.id
        ORDER BY students.id DESC
    """)
    rows = cursor.fetchall()
    columns = ["id", "admission_number", "first_name", "middle_name", "last_name", "dob", "gender", "class"]

    students = []
    for row in rows:
        student = dict(zip(columns, row))
        # Compute full_name
        fn = student["first_name"] or ""
        mn = student["middle_name"] or ""
        ln = student["last_name"] or ""
        student["full_name"] = f"{fn} {mn} {ln}".strip().replace("  ", " ")
        # Compute age
        if student["dob"]:
            dob = datetime.strptime(student["dob"], "%Y-%m-%d")
            today = datetime.today()
            student["Age"] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        else:
            student["Age"] = ""
        students.append(student)

    conn.close()
    return students


def add_student(first_name, middle_name, last_name, dob, gender, class_id):
    admission_number = generate_admission_number()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (admission_number, first_name, middle_name, last_name, dob, gender, class_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (admission_number, first_name.strip(), middle_name.strip(), last_name.strip(), str(dob), gender, class_id))
    conn.commit()
    conn.close()


def update_student(student_id, first_name, middle_name, last_name, dob, gender, class_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students
        SET first_name = ?, middle_name = ?, last_name = ?, dob = ?, gender = ?, class_id = ?
        WHERE id = ?
    """, (first_name.strip(), middle_name.strip(), last_name.strip(), str(dob), gender, class_id, student_id))
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
def get_students_by_class(class_id):
    with sqlite3.connect(DB_NAME) as conn:
        query = """
            SELECT id,
                   (first_name || ' ' || COALESCE(middle_name || ' ', '') || last_name) AS full_name
            FROM students
            WHERE class_id = ?
            ORDER BY full_name
        """
        df = pd.read_sql_query(query, conn, params=(class_id,))
        return df