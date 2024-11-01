import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_client import SiigoAPI
from utils.excel_processor import ExcelProcessor
from utils.scheduler import TaskScheduler
from utils.logger import error_logger
import os
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'api_client' not in st.session_state:
    st.session_state.api_client = None
if 'show_error_details' not in st.session_state:
    st.session_state.show_error_details = False
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = []
if 'current_batch' not in st.session_state:
    st.session_state.current_batch = None

def export_to_excel(data, filename):
    """Export data to Excel file"""
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df = pd.DataFrame(data)
    df.to_excel(writer, index=False, sheet_name='Processing Results')
    writer.close()
    output.seek(0)
    return output

def export_to_csv(data, filename):
    """Export data to CSV file"""
    output = io.StringIO()
    df = pd.DataFrame(data)
    df.to_csv(output, index=False)
    return output.getvalue()

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
        # Export Section
        st.header("Export Processing Results")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export to Excel"):
                if st.session_state.processing_results:
                    output = export_to_excel(
                        st.session_state.processing_results,
                        "processing_results.xlsx"
                    )
                    st.download_button(
                        label="Download Excel File",
                        data=output,
                        file_name="processing_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    error_logger.log_info("Processing results exported to Excel")
                else:
                    st.warning("No processing results available to export")
        
        with col2:
            if st.button("Export to CSV"):
                if st.session_state.processing_results:
                    output = export_to_csv(
                        st.session_state.processing_results,
                        "processing_results.csv"
                    )
                    st.download_button(
                        label="Download CSV File",
                        data=output,
                        file_name="processing_results.csv",
                        mime="text/csv"
                    )
                    error_logger.log_info("Processing results exported to CSV")
                else:
                    st.warning("No processing results available to export")
        
        # Batch Processing Status Dashboard
        st.header("Batch Processing Status")
        
        # Processing Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            total_entries = sum(1 for result in st.session_state.processing_results 
                              if result['status'] == 'Success')
            st.metric("Total Processed", total_entries)
        with col2:
            success_rate = (total_entries / len(st.session_state.processing_results) * 100 
                          if st.session_state.processing_results else 0)
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col3:
            pending_tasks = len([task for task in TaskScheduler().scheduler.get_jobs()])
            st.metric("Pending Tasks", pending_tasks)

        # Current Batch Status
        if st.session_state.current_batch:
            st.subheader("Current Batch Progress")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total = len(st.session_state.current_batch)
            completed = sum(1 for entry in st.session_state.current_batch if entry.get('processed'))
            progress = completed / total if total > 0 else 0
            
            progress_bar.progress(progress)
            status_text.text(f"Processing: {completed}/{total} entries")

        # Recent Processing History
        st.subheader("Recent Processing History")
        if st.session_state.processing_results:
            history_df = pd.DataFrame(st.session_state.processing_results)
            history_df['date'] = pd.to_datetime(history_df['date'])
            history_df = history_df.sort_values('date', ascending=False)
            
            # Apply color coding based on status
            def color_status(status):
                return ['background-color: #ff4b4b' if x == 'Error' 
                        else 'background-color: #00cc00' for x in status]
            
            styled_df = history_df.style.apply(lambda x: color_status(x), 
                                             subset=['status'])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No processing history available")

        # Scheduled Tasks
        st.subheader("Scheduled Tasks")
        scheduler = TaskScheduler()
        jobs = scheduler.scheduler.get_jobs()
        
        if jobs:
            job_data = []
            for job in jobs:
                next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
                job_data.append({
                    "Next Run": next_run,
                    "File": getattr(job.args[0], 'name', 'Unknown'),
                    "Status": "Pending"
                })
            st.dataframe(pd.DataFrame(job_data), use_container_width=True)
        else:
            st.info("No scheduled tasks")

        # File upload section
        st.header("Upload New Batch")
        uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
        
        if uploaded_file:
            try:
                processor = ExcelProcessor(uploaded_file)
                df = processor.read_excel()
                
                st.subheader("Preview of uploaded data")
                st.dataframe(df.head())
                
                if st.button("Process Entries"):
                    with st.spinner("Processing journal entries..."):
                        st.session_state.current_batch = [{'processed': False} for _ in range(len(df))]
                        results = process_entries(df)
                        st.session_state.processing_results.extend(results)
                        st.session_state.current_batch = None
                        display_results(results)
            
            except Exception as e:
                error_logger.log_error(
                    'processing_errors',
                    str(e),
                    {'filename': uploaded_file.name}
                )
                st.error(f"Error processing file: {str(e)}")
        
        # Scheduling section
        st.header("Schedule Processing")
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
    st.session_state.processing_results = []
    st.session_state.current_batch = None

def process_entries(df):
    results = []
    processor = ExcelProcessor(None)
    
    # Group entries by date to create journal entries
    for idx, (date, group) in enumerate(df.groupby('date')):
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
            if st.session_state.current_batch:
                st.session_state.current_batch[idx]['processed'] = True
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
