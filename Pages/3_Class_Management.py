import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from utils.classroom import get_classes, assign_class_teacher
from utils.teacher import get_all_teachers

st.set_page_config(page_title="📚 Class Management", layout="wide")
st.title("📚 Class Management")

# Load data
classes_df = get_classes()
teachers_df = get_all_teachers()

# Filter
class_filter = st.selectbox("📂 Filter by Class", ["All"] + sorted(classes_df["class_name"].unique()))
filtered_df = classes_df.copy()
if class_filter != "All":
    filtered_df = classes_df[classes_df["class_name"] == class_filter]

# === Display Table with Color Coding ===
styled_df = filtered_df.copy()
styled_df["class_teacher"] = styled_df["class_teacher"].fillna("❌ Unassigned")
styled_df["class_teacher_phone"] = styled_df["class_teacher_phone"].fillna("-")

def highlight_teacher(val):
    return "background-color: #d4edda" if val != "❌ Unassigned" else "background-color: #f8d7da"

st.subheader("📋 Class List")
st.dataframe(
    styled_df.style.applymap(highlight_teacher, subset=["class_teacher"]),
    use_container_width=True
)

# === Assign Class Teacher ===
st.divider()
st.subheader("👨‍🏫 Assign/Update Class Teacher")

class_to_assign = st.selectbox("Select Class", classes_df["class_name"])
teacher_options = teachers_df.apply(lambda x: f"{x['id']} - {x['full_name']}", axis=1)
teacher_choice = st.selectbox("Select Teacher", teacher_options)

if st.button("✅ Assign Teacher"):
    class_id = classes_df[classes_df["class_name"] == class_to_assign].iloc[0]["id"]
    teacher_id = int(teacher_choice.split(" - ")[0])
    assign_class_teacher(class_id, teacher_id)
    st.success(f"Class Teacher for {class_to_assign} updated successfully!")
    st.rerun()

# === Pie Chart Visualization ===
st.subheader("📊 Class Size Distribution (Pie Chart)")
fig, ax = plt.subplots()
ax.pie(
    filtered_df["student_count"],
    labels=filtered_df["class_name"],
    autopct="%1.1f%%",
    startangle=90
)
ax.axis("equal")  # Equal aspect ratio ensures pie is a circle.
st.pyplot(fig)

# === Export to Excel ===
def export_excel(df):
    output = io.BytesIO()
    export_df = df[["class_name", "class_teacher", "class_teacher_phone", "student_count"]]
    export_df.to_excel(output, index=False, sheet_name="Classes")
    output.seek(0)
    return output

st.download_button(
    "📥 Export to Excel",
    data=export_excel(filtered_df),
    file_name="classes_export.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)