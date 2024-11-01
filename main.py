import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_client import SiigoAPI
from utils.excel_processor import ExcelProcessor
from utils.scheduler import TaskScheduler
from utils.logger import error_logger
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'api_client' not in st.session_state:
    st.session_state.api_client = None
if 'show_error_details' not in st.session_state:
    st.session_state.show_error_details = False

def main():
    st.title("Siigo Journal Entry Processor")
    
    # Add error monitoring toggle in sidebar
    with st.sidebar:
        if st.session_state.authenticated:
            st.success("Logged in successfully")
            st.button("Logout", on_click=logout)
            st.session_state.show_error_details = st.checkbox("Show Error Details")
            
            # Display error statistics
            st.subheader("Error Statistics")
            stats = error_logger.get_error_stats()
            for error_type, count in stats.items():
                st.metric(error_type.replace('_', ' ').title(), count)
            
            # Show recent errors if enabled
            if st.session_state.show_error_details:
                st.subheader("Recent Errors")
                recent_errors = error_logger.get_recent_errors()
                for error in recent_errors:
                    st.text(error)
    
    # Authentication section
    if not st.session_state.authenticated:
        with st.form("auth_form"):
            username = st.text_input("Username")
            access_key = st.text_input("Access Key", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                try:
                    api_client = SiigoAPI(username, access_key)
                    if api_client.authenticate():
                        st.session_state.authenticated = True
                        st.session_state.api_client = api_client
                        error_logger.log_info(f"User {username} authenticated successfully")
                        st.success("Authentication successful!")
                        st.rerun()
                    else:
                        error_logger.log_error(
                            'authentication_errors',
                            f"Authentication failed for user {username}"
                        )
                        st.error("Authentication failed!")
                except Exception as e:
                    error_logger.log_error(
                        'authentication_errors',
                        str(e),
                        {'username': username}
                    )
                    st.error(f"Authentication error: {str(e)}")
    else:
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
                error_logger.log_error(
                    'processing_errors',
                    str(e),
                    {'filename': uploaded_file.name}
                )
                st.error(f"Error processing file: {str(e)}")
        
        # Scheduling section
        st.subheader("Schedule Processing")
        with st.form("scheduler_form"):
            schedule_time = st.time_input("Select processing time")
            schedule_file = st.file_uploader("Upload Excel file for scheduling", type=['xlsx', 'xls'])
            schedule_submit = st.form_submit_button("Schedule Processing")
            
            if schedule_submit and schedule_file:
                try:
                    scheduler = TaskScheduler()
                    scheduler.schedule_task(schedule_time, schedule_file)
                    error_logger.log_info(
                        f"Processing scheduled for {schedule_time} with file {schedule_file.name}"
                    )
                    st.success(f"Processing scheduled for {schedule_time}")
                except Exception as e:
                    error_logger.log_error(
                        'processing_errors',
                        str(e),
                        {'schedule_time': str(schedule_time), 'filename': schedule_file.name}
                    )
                    st.error(f"Error scheduling task: {str(e)}")

def logout():
    error_logger.log_info("User logged out")
    st.session_state.authenticated = False
    st.session_state.api_client = None

def process_entries(df):
    results = []
    processor = ExcelProcessor(None)
    
    # Group entries by date to create journal entries
    for date, group in df.groupby('date'):
        try:
            entries = processor.format_entries_for_api(group)
            response = st.session_state.api_client.create_journal_entry({
                'date': date.strftime('%Y-%m-%d'),
                'entries': entries
            })
            results.append({
                'date': date.strftime('%Y-%m-%d'),
                'status': 'Success',
                'message': response.get('message', 'Entry processed successfully')
            })
            error_logger.log_info(f"Successfully processed entries for date {date}")
        except Exception as e:
            error_msg = str(e)
            error_logger.log_error(
                'api_errors',
                error_msg,
                {'date': date.strftime('%Y-%m-%d'), 'entries_count': len(group)}
            )
            results.append({
                'date': date.strftime('%Y-%m-%d'),
                'status': 'Error',
                'message': error_msg
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
    
    # Log overall results
    error_logger.log_info(
        f"Processing completed: {success_count} successful, {error_count} failed"
    )

if __name__ == "__main__":
    main()
