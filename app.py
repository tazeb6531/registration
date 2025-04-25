import streamlit as st
import pandas as pd
from datetime import datetime
import socket
import os

class TimesheetApp:
    def __init__(self):
        self.DATA_FILE = "timesheet.csv"
        self.COLUMNS = ["First Name", "Last Name", "Action", "Date", "Time", "IP"]
        self.df = self.load_data()

    def setup_ui(self):
        st.set_page_config(page_title="NCTT LLC")
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image("logo.png", width=80)
        with col2:
            st.markdown("<h1 style='padding-top: 20px;'> NCTT LLC </h1>", unsafe_allow_html=True)

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            df = pd.read_csv(self.DATA_FILE)
            if "Name" in df.columns and "First Name" not in df.columns:
                names = df["Name"].fillna("").str.strip().str.split(" ", n=1, expand=True)
                df["First Name"] = names[0]
                df["Last Name"] = names[1] if names.shape[1] > 1 else ""
                df.drop(columns=["Name"], inplace=True)
            for col in self.COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            df = df[self.COLUMNS]
            df.to_csv(self.DATA_FILE, index=False)
        else:
            df = pd.DataFrame(columns=self.COLUMNS)
        return df

    def handle_form(self):
        with st.form("entry_form", clear_on_submit=True):
            st.markdown("<h4>Enter your First and last name:</h4>", unsafe_allow_html=True)
            first = st.text_input("First Name")
            last = st.text_input("Last Name")
            st.markdown("### Select Action:")
            action = st.radio("Action", ["Sign In", "Lunch Break Out", "Lunch Break In", "Sign Out"], label_visibility="collapsed", horizontal=True)
            submitted = st.form_submit_button("Submit")

        if submitted and first and last:
            now = datetime.now()
            date, time = now.strftime("%Y-%m-%d"), now.strftime("%I:%M:%S %p")
            ip = socket.gethostbyname(socket.gethostname())

            today_entries = self.df[
                (self.df["First Name"] == first) &
                (self.df["Last Name"] == last) &
                (self.df["Date"] == date)
            ]

            if action in today_entries["Action"].values and action in ["Sign In", "Sign Out"]:
                st.warning(f"{action} already recorded today.")
            else:
                new_row = pd.DataFrame([[first, last, action, date, time, ip]], columns=self.COLUMNS)
                self.df = pd.concat([self.df, new_row], ignore_index=True)
                self.df.to_csv(self.DATA_FILE, index=False)
                st.success(f"{action} recorded at {time} on {date}")

    def show_log(self):
        st.subheader("\U0001F4C5 Timesheet Log")
        st.dataframe(self.df)

    def get_rate(self, first, last):
        rates = {
            ("meron", "gebremichal"): 22,
            ("mahider", "nigusie"): 18,
            ("abeham", "mamo"): 14
        }
        return rates.get((first.lower(), last.lower()), 35)

    def compute_weekly_summary(self):
        df = self.df.copy()
        df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
        df.sort_values(by=["First Name", "Last Name", "DateTime"], inplace=True)
        summary = []
        for _, row in df[["First Name", "Last Name"]].drop_duplicates().iterrows():
            fname, lname = row
            person_df = df[(df["First Name"] == fname) & (df["Last Name"] == lname)]
            daily_totals = []
            for date, group in person_df.groupby("Date"):
                actions = group.set_index("Action")["DateTime"].to_dict()
                try:
                    total = actions["Sign Out"] - actions["Sign In"]
                    lunch = actions.get("Lunch Break In", pd.Timedelta(0)) - actions.get("Lunch Break Out", pd.Timedelta(0))
                    hours = (total - lunch).total_seconds() / 3600
                    daily_totals.append({"First Name": fname, "Last Name": lname, "Date": date, "Worked_Hours": hours})
                except KeyError:
                    continue
            if daily_totals:
                daily_df = pd.DataFrame(daily_totals)
                daily_df["Week"] = pd.to_datetime(daily_df["Date"]).dt.to_period("W").astype(str)
                weekly = daily_df.groupby(["First Name", "Last Name", "Week"])["Worked_Hours"].sum().reset_index()
                weekly["Payment"] = weekly["Worked_Hours"] * self.get_rate(fname, lname)
                summary.append(weekly)
        return pd.concat(summary, ignore_index=True) if summary else pd.DataFrame(columns=["First Name", "Last Name", "Week", "Worked_Hours", "Payment"])

    def show_summary(self):
        st.subheader("\U0001F4CA Weekly Summary (Excludes Lunch) with Payment")
        summary_df = self.compute_weekly_summary()
        st.dataframe(summary_df)

    def run(self):
        self.setup_ui()
        self.handle_form()
        self.show_log()
        self.show_summary()

if __name__ == "__main__":
    app = TimesheetApp()
    app.run()
