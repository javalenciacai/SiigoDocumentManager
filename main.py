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
    st.session_state.company_name = None  # Clear company name on logout
    st.rerun()

def get_next_run_preview(schedule_time, frequency, day_of_week=None, day_of_month=None):
    """Get preview of next run time based on schedule parameters"""
    now = datetime.now()
    schedule_datetime = datetime.combine(now.date(), schedule_time)
    
    if schedule_datetime <= now:
        schedule_datetime += timedelta(days=1)
    
    if frequency == "weekly" and day_of_week is not None:
        days_ahead = day_of_week - schedule_datetime.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        schedule_datetime += timedelta(days=days_ahead)
    elif frequency == "monthly" and day_of_month is not None:
        while schedule_datetime.day != day_of_month:
            schedule_datetime += timedelta(days=1)
    
    return schedule_datetime

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
if 'schedule_time' not in st.session_state:
    st.session_state.schedule_time = None
if 'company_name' not in st.session_state:
    st.session_state.company_name = None

def main():
    st.title("Siigo Journal Entry Processor")
    
    # Sidebar content
    with st.sidebar:
        if st.session_state.authenticated:
            st.success("Logged in successfully")
            # Display company name
            if st.session_state.company_name:
                st.markdown(f"### 🏢 {st.session_state.company_name}")
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
                        st.session_state.company_name = api_client.company_name  # Store company name
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
                    
                    # Processing and Scheduling sections in tabs
                    process_tab, schedule_tab = st.tabs(["Process Now", "Schedule Processing"])
                    
                    with process_tab:
                        if st.button("Process Entries", type="primary"):
                            with st.spinner("Processing entries..."):
                                results = process_entries(df)
                                st.session_state.processing_results = results
                                
                                success_count = sum(1 for r in results if r['status'] == 'Success')
                                st.success(f"Processed {len(results)} entries ({success_count} successful)")
                    
                    with schedule_tab:
                        st.markdown("### Schedule Settings")
                        
                        # Enhanced scheduling interface with help text
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            frequency = st.selectbox(
                                "Frequency",
                                ["daily", "weekly", "monthly"],
                                help="How often to process this file"
                            )
                            
                        with col2:
                            # Allow complete time selection without default value
                            hours = st.number_input("Hour (24-hour format)", 
                                                min_value=0, 
                                                max_value=23, 
                                                value=None,
                                                placeholder="Enter hour (0-23)",
                                                help="Enter the hour in 24-hour format")
                            
                            minutes = st.number_input("Minute", 
                                                  min_value=0, 
                                                  max_value=59, 
                                                  value=None,
                                                  placeholder="Enter minute (0-59)",
                                                  help="Enter the minute")
                            
                            # Create time object only when both hours and minutes are set
                            if hours is not None and minutes is not None:
                                schedule_time = datetime.strptime(f"{hours:02d}:{minutes:02d}", "%H:%M").time()
                                st.session_state.schedule_time = schedule_time
                            
                        with col3:
                            if frequency == "weekly":
                                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                                day_index = st.selectbox(
                                    "Day of Week",
                                    range(len(days)),
                                    format_func=lambda x: days[x],
                                    help="Select which day of the week to process"
                                )
                                schedule_params = {'day_of_week': day_index}
                            elif frequency == "monthly":
                                day_of_month = st.selectbox(
                                    "Day of Month",
                                    range(1, 32),
                                    help="Select which day of the month to process"
                                )
                                schedule_params = {'day_of_month': day_of_month}
                            else:
                                schedule_params = {}
                                st.info("File will be processed daily at the specified time")
                        
                        # Preview next run only when time is set
                        if st.session_state.schedule_time:
                            next_run = get_next_run_preview(
                                st.session_state.schedule_time,
                                frequency,
                                day_of_week=schedule_params.get('day_of_week'),
                                day_of_month=schedule_params.get('day_of_month')
                            )
                            
                            st.info(f"📅 Next scheduled run: {next_run.strftime('%A, %B %d, %Y at %I:%M %p')}")
                            
                            # Schedule button with confirmation
                            if st.button("Schedule Processing", type="primary"):
                                try:
                                    scheduler = TaskScheduler()
                                    scheduler.schedule_task(st.session_state.schedule_time, uploaded_file, frequency, **schedule_params)
                                    st.success("✅ Task scheduled successfully!")
                                    
                                    # Show schedule details in a clean format
                                    st.markdown("### Schedule Details")
                                    details = {
                                        "📄 File": uploaded_file.name,
                                        "🔄 Frequency": frequency.capitalize(),
                                        "⏰ Time": st.session_state.schedule_time.strftime("%I:%M %p"),
                                        "📅 Next Run": next_run.strftime("%A, %B %d, %Y at %I:%M %p")
                                    }
                                    if frequency == "weekly":
                                        details["📅 Day"] = days[schedule_params['day_of_week']]
                                    elif frequency == "monthly":
                                        details["📅 Day"] = f"{schedule_params['day_of_month']}th"
                                    
                                    for key, value in details.items():
                                        st.markdown(f"**{key}:** {value}")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error scheduling task: {str(e)}")
                                    error_logger.log_error(
                                        'processing_errors',
                                        f"Error scheduling task: {str(e)}"
                                    )
                        else:
                            st.warning("⚠️ Please set both hour and minute to schedule the task")
                                
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
                
                # Add Cancel buttons for each task
                for idx, task in tasks_df.iterrows():
                    task_id = task['id']
                    if st.button(f"Cancel Task {task_id}"):
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(scheduler.cancel_task(task_id))
                            st.success(f"Task {task_id} cancelled successfully")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error cancelling task: {str(e)}")
            else:
                st.info("No active scheduled tasks")

        # Processed Documents tab
        with tab5:
            st.header("Processed Documents")
            
            # Date filter
            st.subheader("Filter by Date")
            date_filter = st.radio(
                "Date Range",
                ["all", "today", "this_week", "this_month"],
                horizontal=True
            )
            st.session_state.date_filter = date_filter
            
            # Get tasks based on filter
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if date_filter != "all":
                now = datetime.now()
                if date_filter == "today":
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                elif date_filter == "this_week":
                    start_date = now - timedelta(days=now.weekday())
                else:  # this_month
                    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                tasks = loop.run_until_complete(scheduler.get_task_history(
                    None,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=now.strftime('%Y-%m-%d')
                ))
            else:
                tasks = loop.run_until_complete(scheduler.get_task_history(None))
            
            if tasks:
                tasks_df = pd.DataFrame(tasks)
                st.dataframe(tasks_df, use_container_width=True)
            else:
                st.info("No processed documents found for the selected period")

if __name__ == "__main__":
    main()
