import streamlit as st
import pandas as pd
from utils.timetable import (
    get_timetable,
    add_timetable_entry,
    update_timetable_entry,
    delete_timetable_entry,
    get_timetable_entry_by_id
)
from utils.classroom import get_all_classes
from utils.teacher import get_all_teachers
from utils.subject import get_all_subjects
import io

st.title("📅 Timetable & Attendance Management")

# Load mappings
class_df = get_all_classes()
teacher_df = get_all_teachers()
subject_df = get_all_subjects()

class_map = {row["class_name"]: row["id"] for _, row in class_df.iterrows()}
teacher_map = {row["full_name"]: row["id"] for _, row in teacher_df.iterrows()}
subject_map = {row["name"]: row["id"] for _, row in subject_df.iterrows()}

# === Handle filter reset BEFORE widget instantiation ===
if st.session_state.get("clear_filters", False):
    st.session_state["class_filter"] = "All"
    st.session_state["day_filter"] = "All"
    st.session_state["teacher_filter"] = "All"
    st.session_state["start_time_filter"] = pd.to_datetime("00:00").time()
    st.session_state["end_time_filter"] = pd.to_datetime("23:59").time()
    st.session_state["clear_filters"] = False
    st.rerun()

# === Filters ===
st.subheader("🔍 Timetable Filters")

col1, col2 = st.columns(2)
with col1:
    class_filter = st.selectbox("📚 Filter by Class", ["All"] + list(class_map.keys()), key="class_filter")
with col2:
    day_filter = st.selectbox("📅 Filter by Day", ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], key="day_filter")

col3, col4 = st.columns(2)
with col3:
    teacher_filter = st.selectbox("👨‍🏫 Filter by Teacher", ["All"] + list(teacher_map.keys()), key="teacher_filter")
with col4:
    start_time_filter = st.time_input("⏰ Start Time Filter", value=st.session_state.get("start_time_filter", pd.to_datetime("00:00").time()), key="start_time_filter")

end_time_filter = st.time_input("⏰ End Time Filter", value=st.session_state.get("end_time_filter", pd.to_datetime("23:59").time()), key="end_time_filter")

# ✅ Clear Filters Button
if st.button("🔄 Clear All Filters"):
    st.session_state["clear_filters"] = True
    st.rerun()

# === Load and Filter Timetable ===
timetable_df = get_timetable()

if class_filter != "All":
    timetable_df = timetable_df[timetable_df["class"] == class_filter]
if day_filter != "All":
    timetable_df = timetable_df[timetable_df["day"] == day_filter]
if teacher_filter != "All":
    timetable_df = timetable_df[timetable_df["teacher"] == teacher_filter]
if start_time_filter:
    timetable_df = timetable_df[timetable_df["start_time"] >= str(start_time_filter)]
if end_time_filter:
    timetable_df = timetable_df[timetable_df["end_time"] <= str(end_time_filter)]

st.subheader("📋 Timetable Entries")
st.dataframe(timetable_df, use_container_width=True)

# === Excel Export ===
def generate_timetable_excel(dataframe):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    dataframe.to_excel(writer, index=False, sheet_name='Timetable')

    workbook = writer.book
    worksheet = writer.sheets['Timetable']
    header_format = workbook.add_format({
        'bold': True, 'bg_color': '#DCE6F1', 'border': 1
    })

    for col_num, value in enumerate(dataframe.columns.values):
        worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(col_num, col_num, 20)

    writer.close()
    output.seek(0)
    return output

if not timetable_df.empty:
    excel_data = generate_timetable_excel(timetable_df)
    st.download_button(
        label="📥 Download Timetable as Excel",
        data=excel_data,
        file_name="timetable_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# === Entry Form ===
st.subheader("➕ Add / ✏️ Edit Timetable Entry")

edit_id = st.text_input("Entry ID (leave empty to add new)")

with st.form("timetable_form"):
    col1, col2 = st.columns(2)
    with col1:
        class_ = st.selectbox("Class", list(class_map.keys()))
        subject = st.selectbox("Subject", list(subject_map.keys()))
        teacher = st.selectbox("Teacher", list(teacher_map.keys()))
    with col2:
        day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        start_time = st.time_input("Start Time")
        end_time = st.time_input("End Time")

    submitted = st.form_submit_button("✅ Save Entry")

    if submitted:
        if edit_id:
            try:
                update_timetable_entry(
                    entry_id=int(edit_id),
                    class_id=class_map[class_],
                    subject_id=subject_map[subject],
                    teacher_id=teacher_map[teacher],
                    day=day,
                    start_time=str(start_time),
                    end_time=str(end_time)
                )
                st.success("✅ Timetable entry updated.")
            except Exception as e:
                st.error(f"❌ Failed to update entry: {e}")
        else:
            try:
                add_timetable_entry(
                    class_id=class_map[class_],
                    subject_id=subject_map[subject],
                    teacher_id=teacher_map[teacher],
                    day=day,
                    start_time=str(start_time),
                    end_time=str(end_time)
                )
                st.success("✅ Timetable entry added.")
            except Exception as e:
                st.error(f"❌ Failed to add entry: {e}")

# === Delete Entry ===
st.subheader("❌ Delete Timetable Entry")
delete_id = st.text_input("Enter Entry ID to Delete")
if st.button("🗑️ Delete Entry"):
    if delete_id:
        try:
            delete_timetable_entry(int(delete_id))
            st.success(f"✅ Entry {delete_id} deleted.")
        except Exception as e:
            st.error(f"❌ Failed to delete entry: {e}")
    else:
        st.warning("⚠️ Please enter a valid entry ID.")
