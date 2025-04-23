import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ✅ Must be first Streamlit command
st.set_page_config(page_title="🕒 NCTT LLC Timesheet", layout="centered")

st.title("🕒 NCTT LLC Timesheet")

DATA_FILE = "timesheet.csv"

# Load or initialize data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Name", "Action", "Date", "Time"])

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

if action and name:
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%I:%M:%S %p")  # 12-hour format

    new_row = pd.DataFrame([[name, action, date, time]], columns=["Name", "Action", "Date", "Time"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success(f"{action} recorded at {time} on {date}")

st.subheader("📅 Timesheet Log")
st.dataframe(df)
