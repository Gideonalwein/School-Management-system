import streamlit as st
import pandas as pd
import datetime
from utils.student import get_students_by_class
from utils.classroom import get_classes
from utils.attendance import get_attendance_by_date_and_class, mark_attendance

st.set_page_config(page_title="📅 Daily Attendance", layout="wide")
st.title("📅 Daily Class Attendance")

# === Date and Class Selection ===
col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input("Select Date", datetime.date.today())
with col2:
    classes_df = get_classes()
class_options = classes_df.set_index("class_name").to_dict("index")
class_name = st.selectbox("Select Class", list(class_options.keys()))
selected_class_id = class_options[class_name]["id"]


# === Get Students in Class ===
students_df = get_students_by_class(selected_class_id)

if students_df.empty:
    st.warning("No students found for the selected class.")
    st.stop()

# === Load Existing Attendance ===
existing_attendance = get_attendance_by_date_and_class(selected_class_id, selected_date)
status_map = dict(zip(existing_attendance["student_id"], existing_attendance["status"]))

# === Attendance Form with Bulk Assignment ===
st.subheader("🧍 Mark Attendance")

bulk_status = st.selectbox("📌 Mark all students as:", ["Present", "Absent", "Late", "Excused"])

attendance_data = []

st.markdown("### ✏️ Individual Status")

for _, row in students_df.iterrows():
    student_id = row["id"]
    student_name = row["full_name"]
    
    # Use existing status if available, else fallback to bulk selection
    default_status = status_map.get(student_id, bulk_status)

    status = st.radio(
        f"{student_name}",
        ["Present", "Absent", "Late", "Excused"],
        index=["Present", "Absent", "Late", "Excused"].index(default_status),
        horizontal=True,
        key=f"attendance_{student_id}"
    )
    
    attendance_data.append({
        "student_id": student_id,
        "class_id": selected_class_id,
        "date": selected_date,
        "status": status
    })

if st.button("✅ Save Attendance"):
    for record in attendance_data:
        mark_attendance(**record)
    st.success("Attendance saved successfully!")
