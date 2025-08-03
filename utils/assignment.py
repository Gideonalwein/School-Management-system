from utils.db import get_connection
import pandas as pd

def get_teacher_subject_assignments():
    conn = get_connection()
    query = """
    SELECT ts.id, t.first_name || ' ' || t.middle_name || ' ' || t.last_name AS teacher,
           s.name AS subject, c.name AS class
    FROM teacher_subjects ts
    JOIN teachers t ON ts.teacher_id = t.id
    JOIN subjects s ON ts.subject_id = s.id
    JOIN classes c ON ts.class_id = c.id
    """
    return pd.read_sql_query(query, conn)

def assign_teacher_to_subject_class(teacher_id, subject_id, class_id):
    conn = get_connection()
    conn.execute("""
        INSERT INTO teacher_subjects (teacher_id, subject_id, class_id)
        VALUES (?, ?, ?)
    """, (teacher_id, subject_id, class_id))
    conn.commit()

def delete_teacher_assignment(assignment_id):
    conn = get_connection()
    conn.execute("DELETE FROM teacher_subjects WHERE id = ?", (assignment_id,))
    conn.commit()
