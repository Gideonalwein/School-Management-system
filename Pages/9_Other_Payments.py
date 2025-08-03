import streamlit as st
import pandas as pd
import sqlite3
import datetime
import base64
from io import BytesIO
from utils.other_payments import (
    get_all_other_payments,
    add_other_payment,
    update_other_payment,
    delete_other_payment,
    get_student_names_map
)

st.set_page_config(page_title="Other Payments", layout="wide")
st.title("📌 Other Payments Management")

conn = sqlite3.connect("school.db")

# --- FILTERS ---
st.subheader("🔍 Filter Payments")
filters = st.columns(5)
year_filter = filters[0].selectbox("Year", ["All"] + list(range(2022, datetime.datetime.now().year + 1)))
term_filter = filters[1].selectbox("Term", ["All", "Term 1", "Term 2", "Term 3"])
method_filter = filters[2].selectbox("Method", ["All", "Cash", "Bank Transfer", "MPesa", "Cheque"])
category_filter = filters[3].selectbox("Category", ["All", "Transport", "Uniform", "Library Fine", "Other"])
search_name = filters[4].text_input("Search by Student Name")

payments_df = get_all_other_payments()

# --- APPLY FILTERS ---
if year_filter != "All":
    payments_df = payments_df[payments_df["year"] == int(year_filter)]
if term_filter != "All":
    payments_df = payments_df[payments_df["term"] == term_filter]
if method_filter != "All":
    payments_df = payments_df[payments_df["method"] == method_filter]
if category_filter != "All":
    payments_df = payments_df[payments_df["category"] == category_filter]
if search_name:
    payments_df = payments_df[payments_df["student_name"].str.contains(search_name, case=False)]

# --- SUMMARY ---
st.subheader("📊 Summary")
st.write(f"Total Payments: **KES {payments_df['amount_paid'].sum():,.2f}**")
st.dataframe(payments_df, use_container_width=True)

# --- EXPORT ---
def download_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="other_payments.csv">📥 Download CSV</a>'
    return href

st.markdown(download_csv(payments_df), unsafe_allow_html=True)

# --- ADD PAYMENT ---
st.subheader("➕ Add New Payment")
students_map = get_student_names_map()
with st.form("add_payment_form"):
    f1, f2, f3 = st.columns(3)
    student_display = f1.selectbox("Student", list(students_map.keys()))
    category = f2.selectbox("Category", ["Transport", "Uniform", "Library Fine", "Other"])
    amount = f3.number_input("Amount Paid", min_value=0.0, step=0.01)

    f4, f5, f6 = st.columns(3)
    payment_date = f4.date_input("Payment Date", datetime.date.today())
    term = f5.selectbox("Term", ["Term 1", "Term 2", "Term 3"])
    year = f6.selectbox("Year", list(range(2022, datetime.datetime.now().year + 1)))

    f7, f8 = st.columns(2)
    method = f7.selectbox("Payment Method", ["Cash", "Bank Transfer", "MPesa", "Cheque"])
    remarks = f8.text_input("Remarks")

    uploaded_file = st.file_uploader("Upload Receipt (optional)", type=["png", "jpg", "jpeg", "pdf"])

    submitted = st.form_submit_button("Add Payment")
    if submitted:
        student_id = students_map[student_display]
        receipt_blob, receipt_type = None, None
        if uploaded_file:
            receipt_blob = uploaded_file.read()
            receipt_type = uploaded_file.type

        try:
            add_other_payment(student_id, category, amount, str(payment_date), term, year, method, remarks, receipt_blob, receipt_type)
            st.success("Payment added successfully.")
        except Exception as e:
            st.error(f"Failed to add payment: {e}")

# --- DELETE or EDIT ---
st.subheader("✏️ Edit/Delete Payments")
edit_df = payments_df.copy()
selected_row = st.selectbox("Select Payment to Edit/Delete", edit_df.index)
row = edit_df.loc[selected_row]

edit_col1, edit_col2 = st.columns([2, 1])
with edit_col1:
    with st.form("edit_payment_form"):
        student_display = st.selectbox("Student", list(students_map.keys()), index=list(students_map.values()).index(row["student_id"]))
        category = st.selectbox("Category", ["Transport", "Uniform", "Library Fine", "Other"], index=["Transport", "Uniform", "Library Fine", "Other"].index(row["category"]))
        amount = st.number_input("Amount Paid", value=row["amount_paid"])
        payment_date = st.date_input("Payment Date", datetime.datetime.strptime(row["payment_date"], "%Y-%m-%d").date())
        term = st.selectbox("Term", ["Term 1", "Term 2", "Term 3"], index=["Term 1", "Term 2", "Term 3"].index(row["term"]))
        year = st.selectbox("Year", list(range(2022, datetime.datetime.now().year + 1)), index=list(range(2022, datetime.datetime.now().year + 1)).index(row["year"]))
        method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "MPesa", "Cheque"], index=["Cash", "Bank Transfer", "MPesa", "Cheque"].index(row["method"]))
        remarks = st.text_input("Remarks", value=row["description"])
        uploaded_file = st.file_uploader("Replace Receipt (optional)", type=["png", "jpg", "jpeg", "pdf"])

        if st.form_submit_button("Update Payment"):
            receipt_blob, receipt_type = row["receipt"], row["receipt_type"]
            if uploaded_file:
                receipt_blob = uploaded_file.read()
                receipt_type = uploaded_file.type
            try:
                update_other_payment(row["id"], students_map[student_display], category, amount, str(payment_date), term, year, method, remarks, receipt_blob, receipt_type)
                st.success("Payment updated successfully.")
            except Exception as e:
                st.error(f"Error updating: {e}")

with edit_col2:
    if st.button("❌ Delete Payment"):
        try:
            delete_other_payment(row["id"])
            st.success("Payment deleted successfully.")
        except Exception as e:
            st.error(f"Error deleting: {e}")
