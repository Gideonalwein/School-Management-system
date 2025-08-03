import streamlit as st
import pandas as pd
import io
import altair as alt

from utils.subject import get_all_subjects
from utils.teacher import get_all_teachers
from utils.classroom import get_all_classes
from utils.assignment import (
    get_teacher_subject_assignments,
    assign_teacher_to_subject_class,
    delete_teacher_assignment
)

st.set_page_config(layout="wide")
st.title("📘 Teacher-Subject-Class Assignment")

# === Load Data ===
assignments_df = get_teacher_subject_assignments()
teachers = get_all_teachers()
subjects = get_all_subjects()
classes = get_all_classes()

# === Filter UI ===
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        teacher_filter = st.selectbox("👩‍🏫 Filter by Teacher", ["All"] + sorted(assignments_df["teacher"].unique().tolist()))
    with col2:
        subject_filter = st.selectbox("📚 Filter by Subject", ["All"] + sorted(assignments_df["subject"].unique().tolist()))
    with col3:
        class_filter = st.selectbox("🏫 Filter by Class", ["All"] + sorted(assignments_df["class"].unique().tolist()))

# === Apply Filters ===
filtered_df = assignments_df.copy()
if teacher_filter != "All":
    filtered_df = filtered_df[filtered_df["teacher"] == teacher_filter]
if subject_filter != "All":
    filtered_df = filtered_df[filtered_df["subject"] == subject_filter]
if class_filter != "All":
    filtered_df = filtered_df[filtered_df["class"] == class_filter]

# === Export Button ===
def to_excel(df):
    output = io.BytesIO()
    df.to_excel(output, index=False, sheet_name="Assignments")
    output.seek(0)
    return output

if not filtered_df.empty:
    st.download_button(
        label="📥 Export to Excel",
        data=to_excel(filtered_df),
        file_name="teacher_subject_assignments.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# === Color Coding Logic ===
def highlight_rows(row):
    if pd.notna(row['teacher']) and pd.notna(row['subject']) and pd.notna(row['class']):
        return ['background-color: #d0f2d6'] * len(row)  # Light green
    else:
        return ['background-color: #fff3cd'] * len(row)  # Light yellow

# === Display Table with Styling ===
st.markdown("### 📋 Assignment List")
if not filtered_df.empty:
    styled_df = filtered_df.style.apply(highlight_rows, axis=1)
    st.dataframe(styled_df, use_container_width=True)
else:
    st.info("No assignments match your filter.")

# === Charts Section ===
if not assignments_df.empty:
    st.markdown("## 📊 Visualizations")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        subject_chart = (
            alt.Chart(assignments_df)
            .mark_bar()
            .encode(
                x=alt.X("subject:N", title="Subject"),
                y=alt.Y("count():Q", title="Number of Assignments"),
                tooltip=["subject", "count()"]
            )
            .properties(title="Assignments per Subject")
        )
        st.altair_chart(subject_chart, use_container_width=True)

    with chart_col2:
        class_chart = (
            alt.Chart(assignments_df)
            .mark_bar(color="orange")
            .encode(
                x=alt.X("class:N", title="Class"),
                y=alt.Y("count():Q", title="Number of Assignments"),
                tooltip=["class", "count()"]
            )
            .properties(title="Assignments per Class")
        )
        st.altair_chart(class_chart, use_container_width=True)

# === Add New Assignment ===
st.divider()
st.subheader("➕ Assign Teacher to Subject & Class")

teacher_map = {row['full_name']: row['id'] for _, row in teachers.iterrows()}
subject_map = {row['name']: row['id'] for _, row in subjects.iterrows()}
class_map = {row['name']: row['id'] for _, row in classes.iterrows()}

with st.form("assignment_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        teacher = st.selectbox("Teacher", list(teacher_map.keys()))
    with col2:
        subject = st.selectbox("Subject", list(subject_map.keys()))
    with col3:
        class_ = st.selectbox("Class", list(class_map.keys()))

    if st.form_submit_button("Assign"):
        assign_teacher_to_subject_class(
            teacher_map[teacher],
            subject_map[subject],
            class_map[class_]
        )
        st.success("✅ Assignment added successfully.")
        st.rerun()

# === Delete Assignment ===
st.divider()
st.subheader("❌ Remove Assignment")

if len(assignments_df) > 0:
    selected = st.selectbox(
        "Select Assignment to Delete",
        assignments_df.apply(lambda x: f"{x['id']} - {x['teacher']} ({x['subject']} - {x['class']})", axis=1)
    )
    assignment_id = int(selected.split(" - ")[0])
    if st.button("🗑️ Delete Assignment"):
        delete_teacher_assignment(assignment_id)
        st.success("✅ Assignment deleted.")
        st.rerun()
else:
    st.info("ℹ️ No assignments found.")
