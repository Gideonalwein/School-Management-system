import streamlit as st
from datetime import datetime
from PIL import Image
import pytz



# Page setup
st.set_page_config(
    page_title="🏫 School Management System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Set your timezone explicitly
timezone = pytz.timezone("Africa/Nairobi")
now = datetime.now(timezone)
formatted_now = now.strftime("%A, %d %B %Y - %I:%M %p")


# Logo path (adjust as needed)
logo_path = "assets/school_logo.jpg"


# Inject custom CSS for layout and animations
st.markdown("""
    <style>
    .main {
        background-color: #E8F0FE;
        padding: 20px 40px;
        animation: fadeIn 1s ease-in;
    }

    @keyframes fadeIn {
        0% {opacity: 0; transform: translateY(20px);}
        100% {opacity: 1; transform: translateY(0);}
    }

    .header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }

    .logo {
        height: 60px;
        margin-right: 15px;
    }

    .section-header {
        font-size: 22px;
        color: #1f4e79;
        font-weight: 600;
        margin-top: 30px;
    }

    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-top: 10px;
    }

    .card {
        flex: 1 1 calc(20% - 10px);
        min-width: 200px;
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        font-weight: 600;
        font-size: 16px;
        color: #ffffff;
        text-decoration: none;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 3px 3px 14px rgba(0,0,0,0.2);
    }


    /* Background + Text color classes */
    .blue { background-color: #0A400C; color: white; }
    .green { background-color: #4A102A; color: white; }
    .purple { background-color: #F86F03; color: white; }
    .teal { background-color: #8AA624; color: white; }
    .orange { background-color: #17A2B8; color: black; }
    .red { background-color: #FF0060; color: white; }
    .mint { background-color: #47B5FF; color: black; }
    .yellow { background-color: #DC3545; color: black; }
    .indigo { background-color: #386641; color: white; }
    .gray { background-color: #210F37; color: white; }

    a.card {
        display: inline-block;
        color: white !important;
    }

    .welcome-banner {
        background-color: #cfe2f3;
        padding: 10px 15px;
        border-radius: 10px;
        margin-top: 10px;
        font-size: 18px;
        font-weight: 500;
        color: #1f4e79;
    }
    </style>
""", unsafe_allow_html=True)

# Begin main section
st.markdown('<div class="main">', unsafe_allow_html=True)

# Logo + Welcome Banner Section
with st.container():
    col1, col2 = st.columns([1, 6])
    with col1:
        try:
            logo = Image.open(logo_path)
            st.image(logo, use_container_width=False)
        except:
            st.warning("School logo not found. Please upload one at `assets/school_logo.jpg`.")
    with col2:
        st.markdown(f"""
        <div class="welcome-banner">
            👋 Welcome to Mavoko SNP Primary School System &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            📅 {formatted_now}
        </div>
        """, unsafe_allow_html=True)

# --- Dashboard Sections ---

st.markdown("## 🏫 School Management Dashboard")
st.write("Use the sections below to navigate:")

# === STUDENT & TEACHER MANAGEMENT ===
st.markdown('<div class="section-header">🎓 Student & Teacher Management</div>', unsafe_allow_html=True)
st.markdown("""
<div class="card-container">
    <a href="/Student_Management" class="card blue">👨‍🎓 Student Management</a>
    <a href="/Teacher_Management" class="card green">👩‍🏫 Teacher Management</a>
    <a href="/Class_Management" class="card purple">🏫 Class Management</a>
    <a href="/Teacher_Subject_Assignment" class="card teal">📘 Subject Assignment</a>
</div>
""", unsafe_allow_html=True)

# === ATTENDANCE ===
st.markdown('<div class="section-header">🗓️ Attendance & Timetables</div>', unsafe_allow_html=True)
st.markdown("""
<div class="card-container">
    <a href="/Timetable_Attendance" class="card orange">📅 Timetable Attendance</a>
    <a href="/Daily_Attendance" class="card red">📝 Daily Attendance</a>
    <a href="/Attendance_Summary" class="card mint">📊 Attendance Summary</a>
</div>
""", unsafe_allow_html=True)

# === FINANCE ===
st.markdown('<div class="section-header">💰 Finance & Payments</div>', unsafe_allow_html=True)
st.markdown("""
<div class="card-container">
    <a href="/Fee_Management" class="card yellow">💵 Fee Management</a>
    <a href="/Other_Payments" class="card indigo">🧾 Other Payments</a>
    <a href="/Payment_Recording" class="card gray">💼 Payment Recording</a>
    <a href="/Finance_Reports" class="card green">📈 Finance Reports</a>
</div>
""", unsafe_allow_html=True)

# --- Status Info ---
st.markdown("### ℹ️ Status")
st.info("✅ You are connected to the `school.db` database.")

st.markdown("</div>", unsafe_allow_html=True)
