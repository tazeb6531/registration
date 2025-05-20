import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage

# Constants
DATA_FILE = "registration.xlsx"
COLUMNS = ["First Name", "Last Name", "Interest of Training"]
EXCEL_ENGINE = "openpyxl"

# Load or initialize the Excel file
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE, engine=EXCEL_ENGINE)
            df = df.reindex(columns=COLUMNS, fill_value="")
        except Exception as e:
            st.error(f"Error loading Excel file: {e}")
            df = pd.DataFrame(columns=COLUMNS)
    else:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_excel(DATA_FILE, index=False, engine=EXCEL_ENGINE)
    return df

# Save DataFrame to Excel
def save_data(df):
    try:
        df.to_excel(DATA_FILE, index=False, engine=EXCEL_ENGINE)
    except Exception as e:
        st.error(f"Error saving Excel file: {e}")

# Send email with Excel file
def send_email(first, last, interest):
    try:
        email = st.secrets["gmail"]["email"]
        password = st.secrets["gmail"]["password"]

        msg = EmailMessage()
        msg.set_content(f"New Registration:\nFirst Name: {first}\nLast Name: {last}\nInterest: {interest}")
        msg["Subject"] = "New Training Registration (Excel Attached)"
        msg["From"] = email
        msg["To"] = email

        with open(DATA_FILE, "rb") as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype="application",
                               subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               filename=DATA_FILE)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email, password)
            smtp.send_message(msg)

    except Exception as e:
        st.error(f"Email sending failed: {e}")

# Streamlit UI
st.set_page_config(page_title="NCTT LLC - Registration")
col1, col2 = st.columns([1, 4])
with col1:
    st.image("mk_logo.png", width=80)
with col2:
    st.markdown("<h1 style='padding-top: 20px;'>Dallas MK Training Registration</h1>", unsafe_allow_html=True)

# Load existing data
df = load_data()

# Form for registration
with st.form("registration_form", clear_on_submit=True):
    first = st.text_input("First Name")
    last = st.text_input("Last Name")
    interest = st.text_input("Interest of Training (Journalist / Camera / Editing)")
    submitted = st.form_submit_button("Register")

if submitted:
    if first and last and interest:
        new_row = pd.DataFrame([[first, last, interest]], columns=COLUMNS)
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.success(f"Thank you {first} {last} for registering!")
        send_email(first, last, interest)
    else:
        st.warning("Please fill in all fields.")
