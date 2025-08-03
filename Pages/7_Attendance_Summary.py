import streamlit as st
import pandas as pd
import plotly.express as px
from utils.attendance import get_attendance_summary
from utils.classroom import get_classes
import io

st.set_page_config(page_title="📊 Attendance Summary", layout="wide")
st.title("📊 Attendance Summary Dashboard")

# === Load Attendance Summary Data ===
df = get_attendance_summary()

if df.empty:
    st.warning("⚠️ No attendance data available.")
    st.stop()

# Ensure date column is in datetime format
df["date"] = pd.to_datetime(df["date"])

# === Fetch Classes ===
class_df = get_classes()
class_name_map = dict(zip(class_df["class_name"], class_df["id"]))
available_classes = list(class_name_map.keys())

# === Filters ===
col1, col2 = st.columns(2)
with col1:
    selected_class = st.selectbox("📘 Filter by Class", ["All"] + sorted(available_classes))
with col2:
    date_range = st.date_input("📅 Filter by Date Range", [])

# === Apply Filters ===
filtered_df = df.copy()
if selected_class != "All":
    filtered_df = filtered_df[filtered_df["class"] == selected_class]
if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[(filtered_df["date"] >= start_date) & (filtered_df["date"] <= end_date)]

if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()

# === Chart 1: Daily Attendance Trend ===
daily_summary = filtered_df.groupby(["date", "status"]).size().reset_index(name="count")
fig1 = px.bar(
    daily_summary,
    x="date",
    y="count",
    color="status",
    barmode="group",
    title="📅 Daily Attendance Trend"
)
st.plotly_chart(fig1, use_container_width=True)

# === Chart 2: Overall Status Breakdown ===
status_count = filtered_df["status"].value_counts().reset_index()
status_count.columns = ["status", "count"]
fig2 = px.pie(status_count, values="count", names="status", title="🧾 Overall Attendance Breakdown")
st.plotly_chart(fig2, use_container_width=True)

# === Chart 3: Class-wise Status Summary ===
class_summary = filtered_df.groupby(["class", "status"]).size().reset_index(name="count")
fig3 = px.bar(
    class_summary,
    x="class",
    y="count",
    color="status",
    barmode="group",
    title="🏫 Class-wise Attendance Summary"
)
st.plotly_chart(fig3, use_container_width=True)

# === Excel Export Function ===
def generate_excel(dataframe):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    dataframe.to_excel(writer, index=False, sheet_name='Attendance Summary')

    workbook = writer.book
    worksheet = writer.sheets['Attendance Summary']
    header_format = workbook.add_format({'bold': True, 'bg_color': '#DCE6F1', 'border': 1})

    for col_num, value in enumerate(dataframe.columns.values):
        worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(col_num, col_num, 20)

    writer.close()
    output.seek(0)
    return output

# === Download Button ===
excel_data = generate_excel(filtered_df)
st.download_button(
    label="📥 Download Excel Summary",
    data=excel_data,
    file_name="attendance_summary.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
