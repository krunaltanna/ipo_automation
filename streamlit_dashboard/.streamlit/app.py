import streamlit as st
import pandas as pd
import requests
from PIL import Image

# Set the API endpoint URL
API_URL = "https://your-api-endpoint.com/submit-data"

# Initialize session state for form entries and user authentication
if "form_entries" not in st.session_state:
    st.session_state.form_entries = [{"client_id": None, "script": None, "quota": None} for _ in range(20)]

# Dummy credentials for login
USERNAME = "krunal_tanna"
PASSWORD = "test"

# Sidebar with Profile and Logout options
def show_sidebar(): 
    st.sidebar.title("IPO Bulk Apply")

    if "logged_in" in st.session_state and st.session_state.logged_in:
        # Profile icon
        # Show Logout button when logged in
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.success("Logged out successfully!")
            st.rerun()  # Rerun to reload the login page after logout
    else:
        # Show Login button when not logged in
        if st.sidebar.button("Login"):
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            st.rerun()  # Rerun to load the main page after login

# Login Screen (appears if the user is not logged in)
def login_screen():
    st.title("Welcome to IPO Automation Arena!")
    username = st.text_input("Username", "")
    password = st.text_input("Password", "", type="password")

    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            st.rerun()  # Rerun to load the main page after login
        else:
            st.error("Invalid credentials. Try again.")

# Profile Page (only visible when logged in)
def profile_page():
    st.title("Profile Page")
    st.write("Welcome to your profile!")

# Main Form Submission Page (after login)
def form_submission_page():
    st.title("Submit Details")

    # CSV or Excel upload button
    uploaded_file = st.file_uploader("Upload CSV/Excel File", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            data = pd.read_excel(uploaded_file)
        else:
            data = pd.read_csv(uploaded_file)

        # Display initial data preview
        st.write("Data Preview", data.head())

        # Convert the uploaded file's data to form entries (with editable client_id, script, and quota)
        client_ids = data["client_id"].dropna().unique()
        scripts = data["script"].dropna().unique()
        quotas = data["quota"].dropna().unique()

        # Initialize form_entries based on uploaded data
        form_entries = [{"client_id": row["client_id"], "script": row["script"], "quota": row["quota"]} 
                        for index, row in data.iterrows()]

        # Display editable table for each entry
        for i in range(len(form_entries)):
            cols = st.columns(3)
            form_entries[i]["client_id"] = cols[0].text_input(f"Client ID {i+1}", value=form_entries[i]["client_id"])
            form_entries[i]["script"] = cols[1].text_input(f"Script {i+1}", value=form_entries[i]["script"])
            form_entries[i]["quota"] = cols[2].text_input(f"Quota {i+1}", value=form_entries[i]["quota"])

        # Submit button to send data
        if st.button("Submit"):
            # Validate if all fields are filled
            valid_entries = [entry for entry in form_entries if entry["client_id"] and entry["script"] and entry["quota"]]

            if valid_entries:
                # Send data to the API
                response = requests.post(API_URL, json=valid_entries)

                if response.status_code == 200:
                    st.success("Data submitted successfully!")
                    st.session_state.form_entries = [{"client_id": None, "script": None, "quota": None} for _ in range(20)]  # Reset the form after submission
                else:
                    st.error(f"Failed to submit data. Status code: {response.status_code}")
            else:
                st.warning("Please fill in all fields before submitting.")

# Main code logic
def main():
    # Check if the user is logged in
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_screen()
    else:
        # Show the main page after login
        show_sidebar()
        form_submission_page()
        

# Run the app
if __name__ == "__main__":
    main()
