import sqlite3
import pandas as pd

DB_PATH = "school.db"

def get_attendance_by_date_and_class(class_id, date):
    with sqlite3.connect(DB_PATH) as conn:
        query = """
            SELECT * FROM attendance
            WHERE class_id = ? AND date = ?
        """
        return pd.read_sql_query(query, conn, params=(class_id, date))

def mark_attendance(student_id, class_id, date, status):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Check if record exists
        cursor.execute(
            "SELECT id FROM attendance WHERE student_id = ? AND class_id = ? AND date = ?",
            (student_id, class_id, date)
        )
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE attendance SET status = ? WHERE id = ?",
                (status, row[0])
            )
        else:
            cursor.execute(
                "INSERT INTO attendance (student_id, class_id, date, status) VALUES (?, ?, ?, ?)",
                (student_id, class_id, date, status)
            )
        conn.commit()
def get_attendance_summary():
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        a.date,
        s.first_name || ' ' || IFNULL(s.middle_name || ' ', '') || s.last_name AS student_name,
        c.name AS class,
        a.status
    FROM attendance a
    JOIN students s ON a.student_id = s.id
    JOIN classes c ON a.class_id = c.id
    ORDER BY a.date DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
