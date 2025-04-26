import streamlit as st
import pandas as pd
from datetime import datetime
import socket
import os
import smtplib
from email.message import EmailMessage

class TimesheetApp:
    DATA_FILE = "timesheet.csv"
    COLUMNS = ["First Name", "Last Name", "Action", "Date", "Time", "IP"]

    def __init__(self):
        self.df = self.load_data()

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            df = pd.read_csv(self.DATA_FILE)
            df = df.reindex(columns=self.COLUMNS, fill_value="")
        else:
            df = pd.DataFrame(columns=self.COLUMNS)
        df.to_csv(self.DATA_FILE, index=False)
        return df

    def setup_ui(self):
        st.set_page_config(page_title="NCTT LLC")
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image("logo.png", width=80)
        with col2:
            st.markdown("<h1 style='padding-top: 20px;'>NCTT LLC</h1>", unsafe_allow_html=True)

    def send_email(self, subject, body):
        email = st.secrets["gmail"]["email"]
        password = st.secrets["gmail"]["password"]

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = email
        msg['To'] = email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email, password)
            smtp.send_message(msg)

    def handle_form(self):
        with st.form("entry_form", clear_on_submit=True):
            first = st.text_input("First Name")
            last = st.text_input("Last Name")
            action = st.radio(
                "Action",
                ["Sign In", "Lunch Break Out", "Lunch Break In", "Sign Out"],
                horizontal=True,
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("Submit")

        if submitted and first and last:
            now = datetime.now()
            date, time = now.strftime("%Y-%m-%d"), now.strftime("%I:%M:%S %p")
            ip = socket.gethostbyname(socket.gethostname())
            today_entries = self.df.query("`First Name` == @first and `Last Name` == @last and Date == @date")

            if action in today_entries["Action"].values and action in ["Sign In", "Sign Out"]:
                st.warning(f"{action} already recorded today.")
            else:
                new_row = pd.DataFrame([[first, last, action, date, time, ip]], columns=self.COLUMNS)
                self.df = pd.concat([self.df, new_row], ignore_index=True)
                self.df.to_csv(self.DATA_FILE, index=False)
                st.success(f"{action} recorded at {time} on {date}")

                # Send Email Notification
                self.send_email(
                    subject=f"{first} {last} {action}",
                    body=f"{first} {last} did {action} at {time} on {date}. IP: {ip}"
                )

    def show_log(self):
        st.subheader("\U0001F4C5 Timesheet Log")
        st.dataframe(self.df)

    def compute_weekly_summary(self):
        df = self.df.copy()
        df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
        df.sort_values(["First Name", "Last Name", "DateTime"], inplace=True)

        summaries = []
        for (first, last), person_df in df.groupby(["First Name", "Last Name"]):
            daily_hours = []
            for date, group in person_df.groupby("Date"):
                times = group.set_index("Action")["DateTime"].to_dict()
                try:
                    work_duration = times["Sign Out"] - times["Sign In"]
                    lunch_duration = times.get("Lunch Break In", pd.Timedelta(0)) - times.get("Lunch Break Out", pd.Timedelta(0))
                    hours = (work_duration - lunch_duration).total_seconds() / 3600
                    daily_hours.append({"Date": date, "Hours": hours})
                except KeyError:
                    continue
            if daily_hours:
                daily_df = pd.DataFrame(daily_hours)
                daily_df["Week"] = pd.to_datetime(daily_df["Date"]).dt.to_period("W").astype(str)
                weekly = daily_df.groupby("Week")["Hours"].sum().reset_index()
                weekly["First Name"], weekly["Last Name"] = first, last
                weekly["Payment"] = weekly["Hours"] * self.get_rate(first, last)
                summaries.append(weekly)

        return pd.concat(summaries, ignore_index=True) if summaries else pd.DataFrame(columns=["First Name", "Last Name", "Week", "Hours", "Payment"])

    def get_rate(self, first, last):
        rates = {
            ("meron", "gebremichal"): 22,
            ("mahider", "nigusie"): 18,
            ("abeham", "mamo"): 14
        }
        return rates.get((first.lower(), last.lower()), 35)

    def show_summary(self):
        st.subheader("\U0001F4CA Weekly Summary (Excludes Lunch) with Payment")
        st.dataframe(self.compute_weekly_summary())

    def run(self):
        self.setup_ui()
        self.handle_form()
        self.show_log()
        self.show_summary()

if __name__ == "__main__":
    TimesheetApp().run()
