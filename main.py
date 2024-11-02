import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from utils.excel_processor import ExcelProcessor
from utils.scheduler import TaskScheduler
from utils.api_client import SiigoAPI
from utils.logger import error_logger
import os
import asyncio
import time

# Initialize session state variables
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = None
if 'schedule_time' not in st.session_state:
    st.session_state.schedule_time = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'company_name' not in st.session_state:
    st.session_state.company_name = None

# Page config
st.set_page_config(
    page_title="Siigo Document Manager",
    page_icon="assets/logo.svg",
    layout="wide"
)

def get_next_run_preview(time, frequency, day_of_week=None, day_of_month=None):
    """Calculate next run time based on schedule parameters"""
    now = datetime.now()
    schedule_time = datetime.combine(now.date(), time)
    
    if schedule_time <= now:
        schedule_time += timedelta(days=1)
    
    if frequency == "weekly" and day_of_week is not None:
        days_ahead = day_of_week - schedule_time.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        schedule_time += timedelta(days=days_ahead)
    elif frequency == "monthly" and day_of_month is not None:
        if schedule_time.day > day_of_month:
            if schedule_time.month == 12:
                schedule_time = schedule_time.replace(year=schedule_time.year + 1, month=1, day=day_of_month)
            else:
                schedule_time = schedule_time.replace(month=schedule_time.month + 1, day=day_of_month)
        else:
            schedule_time = schedule_time.replace(day=day_of_month)
    
    return schedule_time

def process_entries(df):
    """Process journal entries with company isolation"""
    results = []
    api_client = None
    
    try:
        # Initialize API client with company context
        api_client = SiigoAPI(
            username=os.getenv('SIIGO_USERNAME'),
            access_key=os.getenv('SIIGO_ACCESS_KEY')
        )
        if not api_client.authenticate():
            raise Exception("Authentication failed")
            
        processor = ExcelProcessor(None)  # For data formatting only
        
        # Process entries by document_id
        for doc_id, group in df.groupby('document_id'):
            try:
                # Format entries for API
                payload = processor.format_entries_for_api(group)
                
                # Create journal entry
                response = api_client.create_journal_entry(payload)
                
                results.append({
                    'document_id': doc_id,
                    'status': 'Success',
                    'message': f"Journal entry created successfully"
                })
                
            except Exception as e:
                results.append({
                    'document_id': doc_id,
                    'status': 'Error',
                    'message': str(e)
                })
                
    except Exception as e:
        error_logger.log_error(
            'processing_errors',
            f"Error processing entries: {str(e)}"
        )
        results.append({
            'document_id': 'N/A',
            'status': 'Error',
            'message': f"Processing failed: {str(e)}"
        })
        
    return results

def authenticate():
    """Authenticate user and set company context"""
    try:
        api_client = SiigoAPI(
            username=os.getenv('SIIGO_USERNAME'),
            access_key=os.getenv('SIIGO_ACCESS_KEY')
        )
        
        if api_client.authenticate():
            st.session_state.authenticated = True
            st.session_state.company_name = api_client.company_name
            return True
    except Exception as e:
        error_logger.log_error(
            'authentication_errors',
            f"Authentication error: {str(e)}"
        )
    return False

async def load_scheduled_tasks():
    scheduler = TaskScheduler()
    return await scheduler.get_tasks()

async def load_task_history(task_id):
    scheduler = TaskScheduler()
    return await scheduler.get_task_history(task_id)

async def cancel_scheduled_task(task_id):
    scheduler = TaskScheduler()
    return await scheduler.cancel_task(task_id)

def schedule_processing(file, time, frequency, params):
    scheduler = TaskScheduler()
    scheduler.schedule_task(file, time, frequency, params)

# Main application layout
st.title("Siigo Document Manager")

# Authentication check
if not st.session_state.authenticated:
    st.markdown("### Login")
    username = st.text_input("Username")
    access_key = st.text_input("Access Key", type="password")
    
    if st.button("Login"):
        # Set environment variables
        os.environ['SIIGO_USERNAME'] = username
        os.environ['SIIGO_ACCESS_KEY'] = access_key
        
        if authenticate():
            st.success("✅ Authentication successful!")
            st.info(f"Connected to company: {st.session_state.company_name}")
            time.sleep(2)
            st.rerun()
        else:
            st.error("❌ Authentication failed. Please check your credentials.")
    st.stop()

# Sidebar
with st.sidebar:
    st.image("assets/logo.svg", width=100)
    st.markdown(f"**Company:** {st.session_state.company_name}")
    
    # Error statistics from logger
    st.markdown("### Error Statistics")
    error_stats = error_logger.get_error_stats()
    for error_type, count in error_stats.items():
        st.metric(error_type.replace('_', ' ').title(), count)
    
    # Recent errors
    st.markdown("### Recent Errors")
    recent_errors = error_logger.get_recent_errors(5)
    if recent_errors:
        for error in recent_errors:
            st.error(error.strip())
    else:
        st.success("No recent errors")

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Journal Entry Processing",
    "Catalog Lookup",
    "Processing Status",
    "Scheduled Documents",
    "Processed Documents"
])

with tab1:
    st.markdown("### Upload Journal Entry File")
    uploaded_file = st.file_uploader("Choose Excel file", type=['xlsx'])
    
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
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    frequency = st.selectbox(
                        "Frequency",
                        ["daily", "weekly", "monthly"],
                        help="How often to process this file"
                    )
                    
                with col2:
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
                    
                    if hours is not None and minutes is not None:
                        schedule_time = datetime.strptime(f"{hours:02d}:{minutes:02d}", "%H:%M").time()
                        st.session_state.schedule_time = schedule_time
                    
                with col3:
                    schedule_params = {}
                    if frequency == "weekly":
                        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                        day_index = st.selectbox(
                            "Day of Week",
                            range(len(days)),
                            format_func=lambda x: days[x],
                            help="Select which day of the week to process"
                        )
                        schedule_params['day_of_week'] = day_index
                    elif frequency == "monthly":
                        day_of_month = st.selectbox(
                            "Day of Month",
                            range(1, 32),
                            help="Select which day of the month to process"
                        )
                        schedule_params['day_of_month'] = day_of_month
                    else:
                        st.info("File will be processed daily at the specified time")
                
                if st.session_state.schedule_time:
                    next_run = get_next_run_preview(
                        st.session_state.schedule_time,
                        frequency,
                        day_of_week=schedule_params.get('day_of_week'),
                        day_of_month=schedule_params.get('day_of_month')
                    )
                    
                    st.info(f"📅 Next scheduled run: {next_run.strftime('%A, %B %d, %Y at %I:%M %p')}")
                    
                    if st.button("Schedule Processing", type="primary"):
                        schedule_processing(uploaded_file, st.session_state.schedule_time, frequency, schedule_params)
                else:
                    st.warning("⚠️ Please set both hour and minute to schedule the task")
                    
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

with tab2:
    st.markdown("### Cost Centers and Document Types")
    if st.button("Refresh Catalog Data"):
        try:
            api_client = SiigoAPI(
                username=os.getenv('SIIGO_USERNAME'),
                access_key=os.getenv('SIIGO_ACCESS_KEY')
            )
            if api_client.authenticate():
                # Fetch and display cost centers
                cost_centers = api_client.get_cost_centers()
                if cost_centers:
                    st.markdown("#### Cost Centers")
                    df_cost_centers = pd.DataFrame(cost_centers)
                    st.dataframe(df_cost_centers, use_container_width=True)
                
                # Fetch and display document types
                doc_types = api_client.get_document_types()
                if doc_types:
                    st.markdown("#### Document Types")
                    df_doc_types = pd.DataFrame(doc_types)
                    st.dataframe(df_doc_types, use_container_width=True)
        except Exception as e:
            st.error(f"Error fetching catalog data: {str(e)}")

with tab3:
    st.markdown("### Processing Status")
    
    # Display current processing results if available
    if st.session_state.processing_results:
        results = st.session_state.processing_results
        success_count = sum(1 for r in results if r['status'] == 'Success')
        error_count = len(results) - success_count
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Entries", len(results))
        with col2:
            st.metric("Successful", success_count, delta=success_count)
        with col3:
            st.metric("Failed", error_count, delta=-error_count)
            
        st.markdown("#### Detailed Results")
        for result in results:
            if result['status'] == 'Success':
                st.success(f"Document {result['document_id']}: {result['message']}")
            else:
                st.error(f"Document {result['document_id']}: {result['message']}")
    else:
        st.info("No processing results available. Process some entries to see the status.")

with tab4:
    st.markdown("### Scheduled Documents")
    
    if st.button("Refresh Scheduled Tasks", key="refresh_scheduled"):
        tasks = asyncio.run(load_scheduled_tasks())
        if tasks:
            for task in tasks:
                with st.expander(f"Task {task['id']} - {task['file_name']}"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"**Frequency:** {task['frequency']}")
                    with col2:
                        st.markdown(f"**Next Run:** {task['next_run']}")
                    with col3:
                        st.markdown(f"**Status:** {task['status']}")
                    with col4:
                        if st.button("Cancel Task", key=f"cancel_{task['id']}"):
                            asyncio.run(cancel_scheduled_task(task['id']))
                            st.rerun()
                            
                    # Display task history
                    history = asyncio.run(load_task_history(task['id']))
                    if history:
                        st.markdown("#### Execution History")
                        for entry in history:
                            status_color = "green" if entry['status'] == 'success' else "orange" if entry['status'] == 'partial' else "red"
                            st.markdown(f"- {entry['run_time']}: :{status_color}[{entry['status']}]")
        else:
            st.info("No scheduled tasks found")

with tab5:
    st.markdown("### Processed Documents")
    st.info("Coming soon: View and export processed document history")