from utils.db import get_connection
import pandas as pd

def get_timetable():
    conn = get_connection()
    query = """
    SELECT t.id, c.name AS class, s.name AS subject,
           tr.first_name || ' ' || tr.middle_name || ' ' || tr.last_name AS teacher,
           t.day, t.start_time, t.end_time
    FROM timetable t
    JOIN classes c ON t.class_id = c.id
    JOIN subjects s ON t.subject_id = s.id
    JOIN teachers tr ON t.teacher_id = tr.id
    """
    return pd.read_sql_query(query, conn)

def add_timetable_entry(class_id, subject_id, teacher_id, day, start_time, end_time):
    conn = get_connection()
    conn.execute("""
        INSERT INTO timetable (class_id, subject_id, teacher_id, day, start_time, end_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (class_id, subject_id, teacher_id, day, start_time, end_time))
    conn.commit()

def delete_timetable_entry(entry_id):
    conn = get_connection()
    conn.execute("DELETE FROM timetable WHERE id = ?", (entry_id,))
    conn.commit()
def get_timetable_entry_by_id(entry_id):
    conn = get_connection()
    query = "SELECT * FROM timetable WHERE id = ?"
    df = pd.read_sql_query(query, conn, params=(entry_id,))
    return df.iloc[0] if not df.empty else None


def update_timetable_entry(entry_id, class_id, subject_id, teacher_id, day, start_time, end_time):
    conn = get_connection()
    conn.execute("""
        UPDATE timetable
        SET class_id = ?, subject_id = ?, teacher_id = ?, day = ?, start_time = ?, end_time = ?
        WHERE id = ?
    """, (class_id, subject_id, teacher_id, day, start_time, end_time, entry_id))
    conn.commit()
