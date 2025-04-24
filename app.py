import streamlit as st
import pandas as pd
from datetime import datetime
import socket
import os

# ✅ Must be first Streamlit command
st.set_page_config(page_title="NCTT LLC")

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
    df = pd.DataFrame(columns=["Name", "Action", "Date", "Time", "IP"])

# 📝 Form input
with st.form("entry_form", clear_on_submit=True):
    st.markdown("<h4>Enter your name:</h4>", unsafe_allow_html=True)
    name = st.text_input(label="", placeholder="Your name here")
    st.markdown("### Select Action:")

    col1, col2, col3, col4 = st.columns(4)
    action = st.radio(
        "Action",
        ["Sign In", "Sign Out", "Lunch Break Out", "Lunch Break In"],
        label_visibility="collapsed",
        horizontal=True
    )

    submitted = st.form_submit_button("Submit")

# ✅ Save data if submitted
if submitted and name:
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%I:%M:%S %p")
    ip_address = socket.gethostbyname(socket.gethostname())  # Get computer IP

    new_row = pd.DataFrame([[name, action, date, time, ip_address]],
                           columns=["Name", "Action", "Date", "Time", "IP"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

    st.success(f"{action} recorded at {time} on {date}")

# 📅 Timesheet display
st.subheader("📅 Timesheet Log")
st.dataframe(df)
