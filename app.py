import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ✅ Must be first Streamlit command
st.set_page_config(page_title="NCTT LLC")

# 🔵 Background styling
st.markdown(
    """
    <style>
        .stApp {
            background-color: #e6f0ff;
            padding: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 🖼️ Logo and title on same row
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=80)
with col2:
    st.markdown("<h1 style='padding-top: 20px;'> NCTT LLC </h1>", unsafe_allow_html=True)

# 📄 Load or initialize data
DATA_FILE = "timesheet.csv"
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Name", "Action", "Date", "Time"])

# 👤 User input
name = st.text_input("Enter your name:")
st.markdown("### Select Action:")

col1, col2, col3, col4 = st.columns(4)
action = None

if col1.button("Sign In"):
    action = "Sign In"
elif col2.button("Sign Out"):
    action = "Sign Out"
elif col3.button("Lunch Break Out"):
    action = "Lunch Break Out"
elif col4.button("Lunch Break In"):
    action = "Lunch Break In"

# ✅ Save to CSV
if action and name:
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%I:%M:%S %p")  # 12-hour format

    new_row = pd.DataFrame([[name, action, date, time]], columns=["Name", "Action", "Date", "Time"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success(f"{action} recorded at {time} on {date}")

# 📅 Timesheet display
st.subheader("📅 Timesheet Log")
st.dataframe(df)
