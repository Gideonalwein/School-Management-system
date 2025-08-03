import sqlite3
import pandas as pd
from utils.db import DB_PATH

def get_classes():
    conn = sqlite3.connect(DB_PATH)
    query = '''
        SELECT
            c.id,
            c.name AS class_name,
            c.class_teacher_id,
            t.first_name || ' ' || t.last_name AS class_teacher,
            t.phone AS class_teacher_phone,
            c.max_capacity,
            (
                SELECT COUNT(*) FROM students s WHERE s.class_id = c.id
            ) AS student_count
        FROM classes c
        LEFT JOIN teachers t ON c.class_teacher_id = t.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def assign_class_teacher(class_id, teacher_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE classes SET class_teacher_id = ? WHERE id = ?", (teacher_id, class_id))
    conn.commit()
    conn.close()

def get_all_classes():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT id, name AS class_name FROM classes ORDER BY name;"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def add_class(class_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO classes (name) VALUES (?)", (class_name,))
    conn.commit()
    conn.close()
