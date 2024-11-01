import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_client import SiigoAPI
from utils.excel_processor import ExcelProcessor
from utils.scheduler import TaskScheduler
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'api_client' not in st.session_state:
    st.session_state.api_client = None

def main():
    st.title("Siigo Journal Entry Processor")
    
    # Authentication section
    if not st.session_state.authenticated:
        with st.form("auth_form"):
            username = st.text_input("Username")
            access_key = st.text_input("Access Key", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                api_client = SiigoAPI(username, access_key)
                if api_client.authenticate():
                    st.session_state.authenticated = True
                    st.session_state.api_client = api_client
                    st.success("Authentication successful!")
                    st.rerun()
                else:
                    st.error("Authentication failed!")
    else:
        # Main application interface
        st.sidebar.success("Logged in successfully")
        st.sidebar.button("Logout", on_click=logout)
        
        # File upload section
        uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
        
        if uploaded_file:
            try:
                processor = ExcelProcessor(uploaded_file)
                df = processor.read_excel()
                
                st.subheader("Preview of uploaded data")
                st.dataframe(df.head())
                
                if st.button("Process Entries"):
                    with st.spinner("Processing journal entries..."):
                        results = process_entries(df)
                        display_results(results)
            
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        # Scheduling section
        st.subheader("Schedule Processing")
        with st.form("scheduler_form"):
            schedule_time = st.time_input("Select processing time")
            schedule_file = st.file_uploader("Upload Excel file for scheduling", type=['xlsx', 'xls'])
            schedule_submit = st.form_submit_button("Schedule Processing")
            
            if schedule_submit and schedule_file:
                scheduler = TaskScheduler()
                scheduler.schedule_task(schedule_time, schedule_file)
                st.success(f"Processing scheduled for {schedule_time}")

def logout():
    st.session_state.authenticated = False
    st.session_state.api_client = None

def process_entries(df):
    results = []
    processor = ExcelProcessor(None)  # Create processor instance for data formatting
    
    # Group entries by date to create journal entries
    for date, group in df.groupby('date'):
        entries = processor.format_entries_for_api(group)
        try:
            response = st.session_state.api_client.create_journal_entry({
                'date': date.strftime('%Y-%m-%d'),
                'entries': entries
            })
            results.append({
                'date': date.strftime('%Y-%m-%d'),
                'status': 'Success',
                'message': response.get('message', 'Entry processed successfully')
            })
        except Exception as e:
            results.append({
                'date': date.strftime('%Y-%m-%d'),
                'status': 'Error',
                'message': str(e)
            })
    return results

def display_results(results):
    success_count = sum(1 for r in results if r['status'] == 'Success')
    error_count = len(results) - success_count
    
    st.subheader("Processing Results")
    st.metric("Successful Entries", success_count)
    st.metric("Failed Entries", error_count)
    
    df_results = pd.DataFrame(results)
    st.dataframe(df_results)

if __name__ == "__main__":
    main()
