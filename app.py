import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import socket
import os

# ✅ Setup
st.set_page_config(page_title="NCTT LLC")
DATA_FILE = "timesheet.csv"
COLUMNS = ["First Name", "Last Name", "Action", "Date", "Time", "IP"]

# 🖼️ Header
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=80)
with col2:
    st.markdown("<h1 style='padding-top: 20px;'> NCTT LLC </h1>", unsafe_allow_html=True)

# 📄 Load data with legacy support
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    if "Name" in df.columns and "First Name" not in df.columns:
        split_names = df["Name"].fillna("").str.strip().str.split(pat=" ", n=1, expand=True)
        df["First Name"] = split_names[0]
        df["Last Name"] = split_names[1] if split_names.shape[1] > 1 else ""
        df.drop(columns=["Name"], inplace=True)

        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[COLUMNS]
        df.to_csv(DATA_FILE, index=False)
else:
    df = pd.DataFrame(columns=COLUMNS)

# 📝 Form input
with st.form("entry_form", clear_on_submit=True):
    st.markdown("<h4>Enter Your First and Last Name:</h4>", unsafe_allow_html=True)
    first_name = st.text_input(label="First Name")
    last_name = st.text_input(label="Last Name")
    st.markdown("### Select Action:")
    action = st.radio(
        "Action",
        ["Sign In", "Lunch Break Out", "Lunch Break In", "Sign Out"],
        label_visibility="collapsed",
        horizontal=True
    )
    submitted = st.form_submit_button("Submit")

# 🚫 Duplicate protection
if submitted and first_name and last_name:
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%I:%M:%S %p")
    ip_address = socket.gethostbyname(socket.gethostname())

    today_entries = df[
        (df["First Name"] == first_name) &
        (df["Last Name"] == last_name) &
        (df["Date"] == date)
    ]

    if action in today_entries["Action"].values and action in ["Sign In", "Sign Out"]:
        st.warning(f"{action} already recorded today.")
    else:
        new_row = pd.DataFrame([[first_name, last_name, action, date, time, ip_address]], columns=COLUMNS)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"{action} recorded at {time} on {date}")

# 📅 Timesheet Log
st.subheader("📅 Timesheet Log")
st.dataframe(df)

# 📊 Weekly Summary with Payment
st.subheader("📊 Weekly Summary (Excludes Lunch) with Payment")

def get_rate(first, last):
    if first.lower() == "meron" and last.lower() == "gebremichal":
        return 22
    elif first.lower() == "mahider" and last.lower() == "nigusie":
        return 18
    elif first.lower() == "abeham" and last.lower() == "mamo":
        return 14
    else:
        return 35

def compute_weekly_summary(df):
    df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df.sort_values(by=["First Name", "Last Name", "DateTime"], inplace=True)

    summary = []
    people = df[["First Name", "Last Name"]].drop_duplicates()

    for _, row in people.iterrows():
        fname, lname = row["First Name"], row["Last Name"]
        person_df = df[(df["First Name"] == fname) & (df["Last Name"] == lname)]
        grouped = person_df.groupby("Date")

        daily_totals = []

        for date, group in grouped:
            actions = group.set_index("Action")["DateTime"].to_dict()
            try:
                total_work = actions["Sign Out"] - actions["Sign In"]
                lunch = (actions.get("Lunch Break In", pd.Timedelta(0)) -
                         actions.get("Lunch Break Out", pd.Timedelta(0)))
                worked_time = total_work - lunch
                daily_totals.append({
                    "First Name": fname,
                    "Last Name": lname,
                    "Date": date,
                    "Worked_Hours": worked_time.total_seconds() / 3600
                })
            except KeyError:
                continue  # Skip incomplete days

        daily_df = pd.DataFrame(daily_totals)
        if not daily_df.empty:
            daily_df["Week"] = pd.to_datetime(daily_df["Date"]).dt.to_period("W").astype(str)
            weekly = daily_df.groupby(["First Name", "Last Name", "Week"])["Worked_Hours"].sum().reset_index()

            # Add Payment column
            rate = get_rate(fname, lname)
            weekly["Payment"] = weekly["Worked_Hours"] * rate
            summary.append(weekly)

    if summary:
        return pd.concat(summary, ignore_index=True)
    else:
        return pd.DataFrame(columns=["First Name", "Last Name", "Week", "Worked_Hours", "Payment"])

summary_df = compute_weekly_summary(df)
st.dataframe(summary_df)
