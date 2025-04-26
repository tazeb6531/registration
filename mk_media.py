import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage

# Setup
DATA_FILE = "registration.xlsx"
COLUMNS = ["First Name", "Last Name", "Interest of Training"]

# Load or create the data file
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
    df = df.reindex(columns=COLUMNS, fill_value="")
else:
    df = pd.DataFrame(columns=COLUMNS)
    df.to_excel(DATA_FILE, index=False)

# UI
st.set_page_config(page_title="NCTT LLC - Registration")
col1, col2 = st.columns([1, 4])
with col1:
    st.image("mk_logo.png", width=80)
with col2:
    st.markdown("<h1 style='padding-top: 20px;'>Dallas MK Training Registration</h1>", unsafe_allow_html=True)

# Form
with st.form("registration_form", clear_on_submit=True):
    first = st.text_input("First Name")
    last = st.text_input("Last Name")
    interest = st.text_input("Interest of Training (Journalist / Camera / Editing)")
    submitted = st.form_submit_button("Register")

# Handle form submission
if submitted and first and last and interest:
    new_row = pd.DataFrame([[first, last, interest]], columns=COLUMNS)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)
    st.success(f"Thank you {first} {last} for registering!")

    # Send Email with Excel attachment
    email = st.secrets["gmail"]["email"]
    password = st.secrets["gmail"]["password"]

    msg = EmailMessage()
    msg.set_content(f"New Registration:\nFirst Name: {first}\nLast Name: {last}\nInterest of Training: {interest}")
    msg['Subject'] = "New Training Registration (Excel Attached)"
    msg['From'] = email
    msg['To'] = email

    # Attach the Excel file
    with open(DATA_FILE, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(DATA_FILE)
    msg.add_attachment(file_data, maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email, password)
        smtp.send_message(msg)

# (No display of registration list anymore)
