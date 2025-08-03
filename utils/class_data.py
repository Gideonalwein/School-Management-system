import sqlite3

DB_NAME = "school.db"

def get_all_classes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM classes ORDER BY name")
    rows = cursor.fetchall()
    conn.close()

    class_list = []
    for row in rows:
        class_list.append({"id": row[0], "name": row[1]})
    return class_list

def get_class_by_id(class_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM classes WHERE id = ?", (class_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1]}
    return None

def add_class(name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO classes (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def update_class(class_id, name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE classes SET name = ? WHERE id = ?", (name, class_id))
    conn.commit()
    conn.close()

def delete_class(class_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
    conn.commit()
    conn.close()
def class_name_to_id(class_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM classes WHERE name = ?", (class_name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
    