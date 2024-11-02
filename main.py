import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import asyncio
from utils.api_client import SiigoAPI
from utils.excel_processor import ExcelProcessor
from utils.scheduler import TaskScheduler
from utils.logger import error_logger
import os
from dotenv import load_dotenv
import io
import json

# Load environment variables
load_dotenv()

def fetch_catalogs():
    """Fetch cost centers and document types from Siigo API"""
    try:
        # Fetch cost centers
        cost_centers = st.session_state.api_client.get_cost_centers()
        st.session_state.cost_centers = cost_centers
        
        # Fetch document types
        document_types = st.session_state.api_client.get_document_types()
        st.session_state.document_types = document_types
        
        error_logger.log_info("Successfully fetched catalogs")
    except Exception as e:
        error_logger.log_error(
            'api_errors',
            f"Error fetching catalogs: {str(e)}"
        )
        st.error(f"Error fetching catalogs: {str(e)}")

def process_entries(df):
    """Process journal entries from DataFrame"""
    processor = ExcelProcessor(None)  # Using None as we already have the DataFrame
    try:
        results = []
        for doc_id, group in df.groupby('document_id'):
            try:
                payload = processor.format_entries_for_api(group)
                response = st.session_state.api_client.create_journal_entry(payload)
                results.append({
                    'document_id': doc_id,
                    'status': 'Success',
                    'details': response
                })
            except Exception as e:
                results.append({
                    'document_id': doc_id,
                    'status': 'Failed',
                    'error': str(e)
                })
        return results
    except Exception as e:
        error_logger.log_error(
            'processing_errors',
            f"Error processing entries: {str(e)}"
        )
        raise

def logout():
    """Clear session state and log out user"""
    st.session_state.authenticated = False
    st.session_state.api_client = None
    st.session_state.cost_centers = None
    st.session_state.document_types = None
    st.rerun()

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
if 'cost_centers' not in st.session_state:
    st.session_state.cost_centers = None
if 'document_types' not in st.session_state:
    st.session_state.document_types = None
if 'selected_task' not in st.session_state:
    st.session_state.selected_task = None
if 'date_filter' not in st.session_state:
    st.session_state.date_filter = 'all'

def main():
    st.title("Siigo Journal Entry Processor")
    
    # Sidebar content
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
            
            if st.session_state.show_error_details:
                st.subheader("Recent Errors")
                recent_errors = error_logger.get_recent_errors()
                for error in recent_errors:
                    st.text(error)
                    
                if recent_errors:
                    try:
                        error_text = recent_errors[-1]
                        if 'error_details' in error_text:
                            st.json(json.loads(error_text.split('error_details:', 1)[1]))
                    except:
                        pass
    
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
                        fetch_catalogs()
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
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Journal Entry Processing",
            "Catalog Lookup",
            "Export Results",
            "Processing Status",
            "Processed Documents"
        ])

        # Journal Entry Processing tab
        with tab1:
            st.header("Journal Entry Processing")
            
            # File upload section
            uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx'])
            
            if uploaded_file:
                try:
                    processor = ExcelProcessor(uploaded_file)
                    df = processor.read_excel()
                    st.success("File validated successfully!")
                    
                    st.subheader("Preview")
                    st.dataframe(df.head(), use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Process Entries"):
                            with st.spinner("Processing entries..."):
                                results = process_entries(df)
                                st.session_state.processing_results = results
                                
                                success_count = sum(1 for r in results if r['status'] == 'Success')
                                st.success(f"Processed {len(results)} entries ({success_count} successful)")
                                
                    with col2:
                        # Schedule processing
                        st.subheader("Schedule Processing")
                        schedule_time = st.time_input("Select time")
                        frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])
                        
                        schedule_params = {}
                        if frequency == "weekly":
                            schedule_params['day_of_week'] = st.selectbox("Day of Week", range(7))
                        elif frequency == "monthly":
                            schedule_params['day_of_month'] = st.selectbox("Day of Month", range(1, 32))
                            
                        if st.button("Schedule"):
                            scheduler = TaskScheduler()
                            try:
                                scheduler.schedule_task(schedule_time, uploaded_file, frequency, **schedule_params)
                                st.success("Task scheduled successfully!")
                            except Exception as e:
                                st.error(f"Error scheduling task: {str(e)}")
                                
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")

        # Catalog Lookup tab
        with tab2:
            st.header("Catalog Lookup")
            
            # Add refresh button
            if st.button("Refresh Catalogs"):
                fetch_catalogs()
                st.success("Catalogs refreshed successfully!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Cost Centers")
                if st.session_state.cost_centers:
                    cost_centers_df = pd.DataFrame(st.session_state.cost_centers)
                    st.dataframe(cost_centers_df, use_container_width=True)
                else:
                    st.info("No cost centers loaded")
            
            with col2:
                st.subheader("Document Types")
                if st.session_state.document_types:
                    doc_types_df = pd.DataFrame(st.session_state.document_types)
                    st.dataframe(doc_types_df, use_container_width=True)
                else:
                    st.info("No document types loaded")

        # Export Results tab
        with tab3:
            st.header("Export Results")
            
            if st.session_state.processing_results:
                df = pd.DataFrame(st.session_state.processing_results)
                
                # Display results
                st.subheader("Processing Results")
                st.dataframe(df, use_container_width=True)
                
                # Export options
                export_format = st.selectbox("Export Format", ["Excel", "CSV"])
                
                if st.button("Download Results"):
                    if export_format == "Excel":
                        buffer = io.BytesIO()
                        df.to_excel(buffer, index=False)
                        buffer.seek(0)
                        st.download_button(
                            "Download Excel",
                            buffer,
                            "processing_results.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        buffer = io.StringIO()
                        df.to_csv(buffer, index=False)
                        st.download_button(
                            "Download CSV",
                            buffer.getvalue(),
                            "processing_results.csv",
                            "text/csv"
                        )
            else:
                st.info("No processing results available")

        # Processing Status tab
        with tab4:
            st.header("Processing Status")
            
            # Add refresh button for tasks
            if st.button("Refresh Status"):
                st.rerun()
            
            # Initialize scheduler
            scheduler = TaskScheduler()
            
            # Get scheduled tasks
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = loop.run_until_complete(scheduler.get_scheduled_tasks())
            
            if tasks:
                # Display tasks in a table
                tasks_df = pd.DataFrame(tasks)
                st.dataframe(tasks_df, use_container_width=True)
                
                # Task details
                if st.session_state.selected_task:
                    st.subheader("Task Details")
                    task_history = loop.run_until_complete(
                        scheduler.get_task_history(st.session_state.selected_task)
                    )
                    if task_history:
                        history_df = pd.DataFrame(task_history)
                        st.dataframe(history_df, use_container_width=True)
            else:
                st.info("No scheduled tasks found")

        # Processed Documents tab
        with tab5:
            st.header("Processed Documents")
            
            # Date filter
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                date_filter = st.selectbox(
                    "Date Range",
                    ["Today", "Last 7 Days", "Last 30 Days", "Custom"],
                    key="date_filter"
                )
            
            start_date = None
            end_date = None
            
            if date_filter == "Custom":
                with filter_col2:
                    start_date = st.date_input("Start Date")
                    end_date = st.date_input("End Date")
            else:
                end_date = datetime.now()
                if date_filter == "Today":
                    start_date = end_date.date()
                elif date_filter == "Last 7 Days":
                    start_date = (end_date - timedelta(days=7)).date()
                elif date_filter == "Last 30 Days":
                    start_date = (end_date - timedelta(days=30)).date()
            
            # Get processed documents
            if st.session_state.processing_results:
                filtered_results = [
                    r for r in st.session_state.processing_results
                    if (not start_date or datetime.strptime(r['details']['date'], '%Y-%m-%d').date() >= start_date) and
                    (not end_date or datetime.strptime(r['details']['date'], '%Y-%m-%d').date() <= end_date)
                ]
                
                if filtered_results:
                    # Display summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Documents", len(filtered_results))
                    with col2:
                        success_count = sum(1 for r in filtered_results if r['status'] == 'Success')
                        st.metric("Successful", success_count)
                    with col3:
                        st.metric("Failed", len(filtered_results) - success_count)
                    
                    # Display detailed results
                    st.dataframe(pd.DataFrame(filtered_results), use_container_width=True)
                else:
                    st.info("No documents found for the selected date range")
            else:
                st.info("No processed documents available")

if __name__ == "__main__":
    main()
