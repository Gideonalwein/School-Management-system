import streamlit as st
import pandas as pd
import plotly.express as px
from utils import teacher, subject, class_

st.set_page_config(page_title="Teacher Management", layout="wide")
st.title("👨‍🏫 Teacher Management")

# Load data
teacher_df = teacher.get_all_teachers()
subject_df = subject.get_all_subjects()
class_df = class_.get_all_classes()

# --- FILTERS ---
with st.expander("🔍 Filters", expanded=True):
    col1, col2, col3 = st.columns(3)
    gender_filter = col1.selectbox("Filter by Gender", ["All", "Male", "Female"])
    class_filter = col2.selectbox("Filter by Class", ["All"] + class_df["name"].tolist())
    subject_filter = col3.selectbox("Filter by Subject", ["All"] + subject_df["name"].tolist())

# Apply filters
if gender_filter != "All":
    teacher_df = teacher_df[teacher_df["gender"] == gender_filter]
if class_filter != "All":
    teacher_df = teacher_df[teacher_df["class"] == class_filter]
if subject_filter != "All":
    teacher_df = teacher_df[teacher_df["subject"] == subject_filter]

# --- TEACHERS TABLE ---
st.markdown("### 📋 List of Teachers")
if teacher_df.empty:
    st.info("No teachers found with the selected filters.")
else:
    total_teachers = len(teacher_df)
    male_count = len(teacher_df[teacher_df["gender"] == "Male"])
    female_count = len(teacher_df[teacher_df["gender"] == "Female"])

    st.markdown(f"**👥 Total Teachers: {total_teachers}** | 👨 Male: {male_count} | 👩 Female: {female_count}")
    st.dataframe(teacher_df.drop(columns=["photo"]), use_container_width=True)

# --- ACTION BUTTONS ---
colA1, colA2 = st.columns([1, 1])
with colA1:
    if st.button("➕ Edit/Delete Teacher"):
        st.session_state.edit_teacher_id = None
with colA2:
    selected_id = st.text_input("Enter Teacher ID to Edit/Delete", "")
    if selected_id:
        selected_teacher = teacher.get_teacher_by_id(selected_id)
        if selected_teacher:
            if st.button("✏️ Edit Teacher"):
                st.session_state.edit_teacher_id = int(selected_id)
            if st.button("🗑️ Delete Teacher"):
                teacher.delete_teacher(int(selected_id))
                st.success("Teacher deleted successfully.")
                st.rerun()

# --- TEACHER FORM ---
subject_names = subject_df["name"].tolist()
class_names = class_df["name"].tolist()
gender_options = ["Male", "Female"]

if "edit_teacher_id" in st.session_state:
    edit_mode = st.session_state.edit_teacher_id is not None
    data = teacher.get_teacher_by_id(st.session_state.edit_teacher_id) if edit_mode else {}
    st.markdown("---")
    with st.form("teacher_form", clear_on_submit=not edit_mode):
        st.subheader("✍️ Edit Teacher" if edit_mode else "➕ Add New Teacher")

        col1, col2, col3 = st.columns(3)
        first_name = col1.text_input("First Name*", value=data.get("first_name", ""))
        middle_name = col2.text_input("Middle Name*", value=data.get("middle_name", ""))
        last_name = col3.text_input("Last Name*", value=data.get("last_name", ""))

        col4, col5, col6 = st.columns(3)
        hire_date = col4.date_input("Hire Date*", value=pd.to_datetime(data.get("hire_date", pd.Timestamp.now())))
        phone = col5.text_input("Phone Number*", value=data.get("phone", ""))
        gender = col6.selectbox("Gender*", gender_options, index=gender_options.index(data.get("gender", "Male")))

        col7, col8 = st.columns(2)
        subject_name = col7.selectbox("Subject*", subject_names, index=subject_names.index(data.get("subject", subject_names[0])) if data.get("subject") else 0)
        class_name = col8.selectbox("Class*", class_names, index=class_names.index(data.get("class", class_names[0])) if data.get("class") else 0)

        photo = st.file_uploader("Upload Teacher Photo*", type=["png", "jpg", "jpeg"])
        photo_data = photo.read() if photo else data.get("photo", None)

        submit = st.form_submit_button("✅ Submit")

        if submit:
            if not all([first_name, middle_name, last_name, phone, photo_data]):
                st.warning("All fields are required.")
            else:
                if edit_mode:
                    teacher.update_teacher(
                        st.session_state.edit_teacher_id,
                        first_name, middle_name, last_name,
                        hire_date.strftime("%Y-%m-%d"), phone, photo_data,
                        gender, subject_name, class_name
                    )
                    st.success("Teacher updated successfully.")
                    del st.session_state.edit_teacher_id
                else:
                    teacher.add_teacher(
                        first_name, middle_name, last_name,
                        hire_date.strftime("%Y-%m-%d"), phone, photo_data,
                        gender, subject_name, class_name
                    )
                    st.success("Teacher added successfully.")
                st.rerun()

# --- PIE CHARTS ---
st.markdown("---")
st.subheader("📊 Teacher Distribution")

colP1, colP2 = st.columns(2)

with colP1:
    gender_chart = px.pie(teacher_df, names="gender", title="Gender Distribution", hole=0.3)
    st.plotly_chart(gender_chart, use_container_width=True)

with colP2:
    subject_chart = px.pie(teacher_df, names="subject", title="Subject Distribution", hole=0.3)
    st.plotly_chart(subject_chart, use_container_width=True)
