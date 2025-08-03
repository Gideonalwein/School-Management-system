import streamlit as st
import pandas as pd
from datetime import datetime
from utils.student import get_all_students, add_student, update_student, delete_student
from utils.class_data import get_all_classes
import plotly.express as px

st.set_page_config(page_title="Student Management", layout="wide")
st.title("👨‍🎓 Student Management")

# ------------------------------
# 📦 Load Data
# ------------------------------
students_df = pd.DataFrame(get_all_students())
classes = get_all_classes()
class_name_to_id = {c['name']: c['id'] for c in classes}
class_id_to_name = {v: k for k, v in class_name_to_id.items()}

# Preprocess data
if not students_df.empty:
    students_df["Gender"] = students_df["gender"].fillna("Unknown")
    students_df["Class"] = students_df["class"].fillna("Unassigned")
    students_df["dob"] = pd.to_datetime(students_df["dob"], errors='coerce')
    students_df["Year"] = students_df["dob"].dt.year

# ------------------------------
# 🔍 Filter Section
# ------------------------------
with st.expander("🔍 Filter Students"):
    name_filter = st.text_input("Search by Name").lower()
    gender_filter = st.selectbox("Filter by Gender", ["All", "Male", "Female"])
    class_filter = st.selectbox("Filter by Class", ["All"] + list(class_name_to_id.keys()))

    filtered_df = students_df.copy()
    if name_filter:
        filtered_df = filtered_df[filtered_df["full_name"].str.lower().str.contains(name_filter)]
    if gender_filter != "All":
        filtered_df = filtered_df[filtered_df["Gender"] == gender_filter]
    if class_filter != "All":
        filtered_df = filtered_df[filtered_df["Class"] == class_filter]

# ------------------------------
# 📋 Display Table
# ------------------------------
st.subheader("📋 Student Records")
if not filtered_df.empty:
    st.dataframe(filtered_df[["admission_number", "full_name", "Gender", "Class", "Age"]])
else:
    st.info("No students match the filter criteria.")
st.markdown(f"**Total Students:** {len(filtered_df)}")
st.markdown("---")

# ------------------------------
# 📊 Charts and Insights
# ------------------------------
st.subheader("📊 Student Insights")
if not students_df.empty:
    c1, c2 = st.columns(2)
    with c1:
        gender_counts = students_df["Gender"].value_counts().reset_index()
        gender_counts.columns = ["Gender", "Count"]
        fig1 = px.pie(gender_counts, names='Gender', values='Count',
                      title='Gender Distribution', hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        class_counts = students_df["Class"].value_counts().reset_index()
        class_counts.columns = ["Class", "Count"]
        fig2 = px.pie(class_counts, names='Class', values='Count',
                      title='Class Distribution', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 📈 Student Trends")

    trend_col1, trend_col2 = st.columns(2)

    with trend_col1:
        bar = px.bar(class_counts, x='Class', y='Count',
                     title="Number of Students per Class",
                     text_auto=True)
        st.plotly_chart(bar, use_container_width=True)

    with trend_col2:
        if "Year" in students_df.columns and not students_df["Year"].isna().all():
            year_counts = students_df["Year"].value_counts().sort_index().reset_index()
            year_counts.columns = ["Year", "Count"]
            line = px.line(year_counts, x="Year", y="Count", markers=True,
                           title="Students Added by Year")
            st.plotly_chart(line, use_container_width=True)
        else:
            st.info("Year of Birth data is missing or invalid for trend chart.")

st.markdown("---")

# ------------------------------
# ✏️ Student Form Section
# ------------------------------
st.subheader("✏️ Add / Edit / Delete Student")

# Build dropdown: "➕ New Student" + full name + adm no
student_options = ["➕ New Student"] + [
    f"{row['admission_number']} - {row['full_name']}" for _, row in students_df.iterrows()
]
selected_label = st.selectbox("Select Student", student_options)

# Determine whether editing or adding
editing = selected_label != "➕ New Student"
student_data = {}

if editing:
    adm_no = selected_label.split(" - ")[0]
    selected_student = students_df[students_df["admission_number"] == adm_no].iloc[0]
    student_data = selected_student.to_dict()
    student_id = student_data.get("id")
else:
    student_id = None

# Input fields
first_name = st.text_input("First Name", student_data.get("first_name", ""))
middle_name = st.text_input("Middle Name", student_data.get("middle_name", ""))
last_name = st.text_input("Last Name", student_data.get("last_name", ""))
dob = st.date_input("Date of Birth", pd.to_datetime(student_data.get("dob", datetime.today())))
gender = st.selectbox("Gender", ["Male", "Female"], index=["Male", "Female"].index(student_data.get("gender", "Male")))
selected_class = st.selectbox("Class", list(class_name_to_id.keys()), index=list(class_name_to_id.keys()).index(student_data.get("class", list(class_name_to_id.keys())[0])))

# ------------------------------
# 🔘 Action Buttons
# ------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Save"):
        if not first_name or not last_name:
            st.warning("⚠️ First and last name are required.")
        else:
            class_id = class_name_to_id[selected_class]
            if editing:
                update_student(student_id, first_name, middle_name, last_name, dob, gender, class_id)
                st.success("✅ Student updated.")
            else:
                add_student(first_name, middle_name, last_name, dob, gender, class_id)
                st.success("✅ Student added.")
            st.rerun()

with col2:
    if editing and st.button("🗑️ Delete"):
        delete_student(student_id)
        st.success("🗑️ Student deleted.")
        st.rerun()

with col3:
    if st.button("🔄 Refresh"):
        st.rerun()
