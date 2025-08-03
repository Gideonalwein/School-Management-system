import sqlite3
import streamlit as st
import pandas as pd
import io
import plotly.express as px
from fpdf import FPDF
from utils.fees import (
    get_fee_structures,
    get_fee_payments,
    add_fee_structure,
    delete_fee_structure,
    add_fee_payment,
    delete_fee_payment,
    get_student_fee_summary,
    get_fee_summary
)

st.set_page_config(layout="wide")
st.title("💰 Fee & Finance Management")

# --- Initialize session state for filters ---
if "reset_filters" not in st.session_state:
    st.session_state.reset_filters = False
if "selected_class" not in st.session_state:
    st.session_state.selected_class = "All"
if "selected_term" not in st.session_state:
    st.session_state.selected_term = "All"
if "selected_year" not in st.session_state:
    st.session_state.selected_year = "All"
if "selected_method" not in st.session_state:
    st.session_state.selected_method = "All"
if "start_date" not in st.session_state:
    st.session_state.start_date = None
if "end_date" not in st.session_state:
    st.session_state.end_date = None

if st.session_state.reset_filters:
    st.session_state.selected_class = "All"
    st.session_state.selected_term = "All"
    st.session_state.selected_year = "All"
    st.session_state.selected_method = "All"
    st.session_state.start_date = None
    st.session_state.end_date = None
    st.session_state.reset_filters = False
    st.rerun()

# --- Fee Structures ---
st.subheader("📋 Fee Structures")
fee_structures = get_fee_structures()
if not fee_structures.empty:
    st.dataframe(fee_structures, use_container_width=True)

with st.expander("➕ Add New Fee Structure"):
    with st.form("add_fee_structure_form"):
        level = st.text_input("Level/Class")
        amount = st.number_input("Fee Amount", min_value=0)
        year = st.number_input("Applicable Year", min_value=2020, step=1, value=2025)
        term = st.selectbox("Applicable Term", ["Term 1", "Term 2", "Term 3"])
        if st.form_submit_button("Add"):
            add_fee_structure(level, amount, year, term)
            st.success("✅ Fee structure added.")
            st.rerun()

st.divider()

# --- Fee Payments ---
st.subheader("💳 Fee Payments")

classes = get_fee_structures()["level"].unique().tolist()
terms = ["All"] + sorted(fee_structures["term"].unique())
years = ["All"] + sorted(fee_structures["year"].astype(str).unique(), reverse=True)
payment_methods = ["All", "Cash", "MPesa", "Bank"]

col1, col2, col3 = st.columns(3)
with col1:
    st.session_state.selected_class = st.selectbox("Filter by Class Level", ["All"] + classes, index=(["All"] + classes).index(st.session_state.selected_class) if st.session_state.selected_class in classes else 0)
with col2:
    st.session_state.selected_term = st.selectbox("Filter by Term", options=terms, index=terms.index(st.session_state.selected_term) if st.session_state.selected_term in terms else 0)
with col3:
    st.session_state.selected_year = st.selectbox("Filter by Year", options=years, index=years.index(st.session_state.selected_year) if st.session_state.selected_year in years else 0)

col4, col5 = st.columns(2)
with col4:
    st.session_state.selected_method = st.selectbox("Filter by Method", options=payment_methods, index=payment_methods.index(st.session_state.selected_method) if st.session_state.selected_method in payment_methods else 0)
with col5:
    if st.button("🧹 Clear All Filters"):
        st.session_state.reset_filters = True
        st.rerun()

start_date = st.date_input("Start Date", value=st.session_state.start_date, key="start_date")
end_date = st.date_input("End Date", value=st.session_state.end_date, key="end_date")

payments = get_fee_payments(class_level=None if st.session_state.selected_class == "All" else st.session_state.selected_class)

# Apply filters
if st.session_state.selected_term != "All":
    payments = payments[payments["term"] == st.session_state.selected_term]
if st.session_state.selected_year != "All":
    payments = payments[payments["year"].astype(str) == st.session_state.selected_year]
if st.session_state.selected_method != "All":
    payments = payments[payments["method"] == st.session_state.selected_method]
if start_date:
    payments = payments[payments["payment_date"] >= pd.to_datetime(start_date).strftime("%Y-%m-%d")]
if end_date:
    payments = payments[payments["payment_date"] <= pd.to_datetime(end_date).strftime("%Y-%m-%d")]

if not payments.empty:
    def to_excel(df):
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return output

    st.download_button("📥 Export Payments", to_excel(payments), file_name="fee_payments.xlsx")
    st.dataframe(payments, use_container_width=True)

    chart_data = payments.groupby("student_name")["amount_paid"].sum().reset_index()
    fig = px.bar(chart_data, x="student_name", y="amount_paid", title="Total Payments by Student")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No payment records found.")

# --- Record Payment ---
with st.expander("➕ Record New Payment"):
    with st.form("add_fee_payment_form"):

        students_df = pd.read_sql_query(
            "SELECT id, first_name || ' ' || middle_name || ' ' || last_name AS student_name FROM students",
            sqlite3.connect("school.db")
        )
        student_names = students_df["student_name"].tolist()
        selected_name = st.selectbox("Select Student", student_names)

        student_id = students_df[students_df["student_name"] == selected_name]["id"].values[0]

        amount = st.number_input("Amount Paid", min_value=0)
        payment_date = st.date_input("Payment Date")
        method_options = ["Cash", "Bank Transfer", "MPesa", "Cheque"]
        method = st.selectbox("Payment Method", method_options)
        term = st.selectbox("Term", ["Term 1", "Term 2", "Term 3"])
        year = st.number_input("Year", min_value=2020, step=1, value=2025)

        if st.form_submit_button("Record Payment"):
            try:
                add_fee_payment(student_id, amount, payment_date.isoformat(), method, term, year)
                st.success("✅ Payment recorded.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to record payment: {e}")

st.divider()

# --- Fee Summary + Statement Section ---
st.subheader("📊 Fee Balance Summary")
summary = get_student_fee_summary()
if not summary.empty:
    selected_student = st.selectbox("🧑 Select Student for Statement", options=summary["student_name"].unique())
    student_data = summary[summary["student_name"] == selected_student].iloc[0]
    student_payments = payments[payments["student_name"] == selected_student]

    st.markdown(f"### Statement for **{selected_student}**")
    st.dataframe(student_payments, use_container_width=True)

    total_expected = student_data["expected_fee"]
    total_paid = student_data["amount_paid"]
    balance = student_data["balance"]

    st.markdown(f"**Total Expected:** KES {total_expected:,.0f}  \n**Total Paid:** KES {total_paid:,.0f}  \n**Balance:** KES {balance:,.0f}")

    def generate_pdf(student_data, payment_df):
        pdf = FPDF()
        pdf.add_page()
        try:
            pdf.image("assets/logo.png", x=10, y=8, w=30)
        except:
            pass

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "My School Name", ln=True, align="C")
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Fee Statement for {student_data['student_name']}", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Class: {student_data['class_level']}", ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(40, 10, "Date")
        pdf.cell(40, 10, "Method")
        pdf.cell(40, 10, "Term")
        pdf.cell(40, 10, "Amount", ln=True)
        pdf.set_font("Arial", "", 12)

        for _, row in payment_df.iterrows():
            pdf.cell(40, 10, row["payment_date"])
            pdf.cell(40, 10, row["method"])
            pdf.cell(40, 10, row["term"])
            pdf.cell(40, 10, f"KES {row['amount_paid']:,.0f}", ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Total Expected: KES {student_data['expected_fee']:,.0f}", ln=True)
        pdf.cell(0, 10, f"Total Paid: KES {student_data['amount_paid']:,.0f}", ln=True)
        pdf.cell(0, 10, f"Balance: KES {student_data['balance']:,.0f}", ln=True)

        pdf.ln(10)
        term_summary = payment_df.groupby(["year", "term"])["amount_paid"].sum().reset_index()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Term Breakdown", ln=True)
        pdf.set_font("Arial", "", 12)
        for _, row in term_summary.iterrows():
            pdf.cell(0, 10, f"{row['term']} {row['year']}: KES {row['amount_paid']:,.0f}", ln=True)

        pdf.ln(20)
        pdf.cell(0, 10, "_________________________", ln=True)
        pdf.cell(0, 10, "Headteacher Signature", ln=True)

        return pdf.output(dest="S").encode("latin1")

    if st.button("📄 Generate Statement PDF"):
        st.download_button(
            label="⬇️ Download PDF",
            data=generate_pdf(student_data, student_payments),
            file_name=f"{selected_student}_Fee_Statement.pdf",
            mime="application/pdf"
        )
else:
    st.info("No summary data available.")
