import streamlit as st
import pandas as pd
from datetime import datetime, time
import time as time_module
from utils.excel_processor import ExcelProcessor
from utils.api_client import SiigoAPI
from utils.scheduler import TaskScheduler
import os
import asyncio

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'api_client' not in st.session_state:
    st.session_state.api_client = None
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = TaskScheduler()
if 'schedule_time' not in st.session_state:
    st.session_state.schedule_time = time(9, 0)  # Default to 9:00 AM

def authenticate():
    """Authenticate with Siigo API"""
    username = os.getenv('SIIGO_USERNAME')
    access_key = os.getenv('SIIGO_ACCESS_KEY')
    
    if not username or not access_key:
        st.error("Missing credentials. Please check environment variables.")
        return False
        
    api_client = SiigoAPI(username, access_key)
    if api_client.authenticate():
        st.session_state.authenticated = True
        st.session_state.api_client = api_client
        return True
    return False

def process_entries(df):
    """Process journal entries"""
    results = []
    for doc_id, group in df.groupby('document_id'):
        try:
            payload = ExcelProcessor(None).format_entries_for_api(group)
            response = st.session_state.api_client.create_journal_entry(payload)
            results.append({
                'document_id': doc_id,
                'status': 'Success',
                'response': response
            })
        except Exception as e:
            results.append({
                'document_id': doc_id,
                'status': 'Failed',
                'error': str(e)
            })
    return results

def schedule_processing(file, time, frequency='daily', params=None):
    """Schedule file processing"""
    if not st.session_state.authenticated:
        raise Exception("Authentication required")
        
    if not file:
        raise Exception("File required")
        
    # Schedule the task
    schedule_info = st.session_state.scheduler.schedule_task(
        time=time,
        file=file,
        company_name=st.session_state.api_client.company_name,
        frequency=frequency,
        day_of_week=params.get('day_of_week') if params else None,
        day_of_month=params.get('day_of_month') if params else None
    )
    
    return schedule_info

async def load_scheduled_tasks():
    """Load scheduled tasks from database"""
    if st.session_state.authenticated:
        return await st.session_state.scheduler.get_scheduled_tasks(
            st.session_state.api_client.company_name
        )
    return []

def main():
    st.set_page_config(
        page_title="Siigo Journal Entry Processor",
        page_icon="📊",
        layout="wide"
    )
    
    # Authentication check and login form
    if not st.session_state.authenticated:
        st.title("🔐 Login to Siigo API")
        username = st.text_input("Username")
        access_key = st.text_input("Access Key", type="password")
        
        if st.button("Login"):
            os.environ['SIIGO_USERNAME'] = username
            os.environ['SIIGO_ACCESS_KEY'] = access_key
            
            if authenticate():
                st.success("✅ Authentication successful!")
                st.info(f"Connected to company: {st.session_state.api_client.company_name}")
                time_module.sleep(2)
                st.rerun()
            else:
                st.error("❌ Authentication failed. Please check your credentials.")
        st.stop()  # Don't show rest of UI until authenticated
        
    # Main interface
    st.title(f"📊 Siigo Journal Entry Processor")
    st.caption(f"Connected as: {st.session_state.api_client.company_name}")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Journal Entry Processing",
        "Scheduled Documents",
        "Processing Status",
        "Processed Documents"
    ])
    
    # Journal Entry Processing Tab
    with tab1:
        st.header("Upload and Process")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls'],
            help="Upload your journal entries Excel file"
        )
        
        if uploaded_file:
            try:
                processor = ExcelProcessor(uploaded_file)
                df = processor.read_excel()
                
                st.success("✅ File validated successfully!")
                
                # Display preview
                with st.expander("Preview Data"):
                    st.dataframe(df)
                    
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Process Now")
                    if st.button("Process Entries", type="primary"):
                        with st.spinner("Processing entries..."):
                            results = process_entries(df)
                            
                            # Display results
                            success_count = sum(1 for r in results if r['status'] == 'Success')
                            st.write(f"Processed {len(results)} documents:")
                            st.write(f"- ✅ {success_count} successful")
                            st.write(f"- ❌ {len(results) - success_count} failed")
                            
                            # Show detailed results
                            with st.expander("Detailed Results"):
                                for result in results:
                                    if result['status'] == 'Success':
                                        st.success(f"Document {result['document_id']}: Success")
                                    else:
                                        st.error(
                                            f"Document {result['document_id']}: Failed\n"
                                            f"Error: {result['error']}"
                                        )
                                        
                with col2:
                    st.subheader("Schedule Processing")
                    frequency = st.selectbox(
                        "Frequency",
                        ['daily', 'weekly', 'monthly'],
                        help="Select how often to process this file"
                    )
                    
                    schedule_params = {}
                    
                    if frequency == 'weekly':
                        schedule_params['day_of_week'] = st.selectbox(
                            "Day of Week",
                            range(7),
                            format_func=lambda x: ['Monday', 'Tuesday', 'Wednesday',
                                               'Thursday', 'Friday', 'Saturday',
                                               'Sunday'][x]
                        )
                    elif frequency == 'monthly':
                        schedule_params['day_of_month'] = st.selectbox(
                            "Day of Month",
                            range(1, 29)  # Avoid 29-31 for consistency
                        )
                        
                    st.session_state.schedule_time = st.time_input(
                        "Processing Time",
                        value=st.session_state.schedule_time
                    )
                    
                    if st.button("Schedule Processing", type="primary"):
                        try:
                            schedule_info = schedule_processing(
                                file=uploaded_file,
                                time=st.session_state.schedule_time,
                                frequency=frequency,
                                params=schedule_params
                            )
                            st.success(f"✅ Task scheduled successfully! Next run at {schedule_info['next_run']}")
                            st.balloons()  # Add celebratory animation
                        except Exception as e:
                            st.error(f"Error scheduling task: {str(e)}")
                            
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                
    # Scheduled Documents Tab
    with tab2:
        st.header("Scheduled Documents")
        
        if st.button("Refresh"):
            st.rerun()
            
        # Load scheduled tasks
        tasks = asyncio.run(load_scheduled_tasks())
        
        if tasks:
            for task in tasks:
                with st.expander(f"📄 {task['file_name']} - Next run: {task['next_run']}"):
                    st.write(f"Frequency: {task['frequency'].title()}")
                    if task['frequency'] == 'weekly':
                        st.write(f"Day: {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][task['day_of_week']]}")
                    elif task['frequency'] == 'monthly':
                        st.write(f"Day: {task['day_of_month']}")
                        
                    # Add cancel button
                    if st.button("Cancel Schedule", key=f"cancel_{task['id']}"):
                        try:
                            asyncio.run(st.session_state.scheduler.cancel_task(
                                task['id'],
                                st.session_state.api_client.company_name
                            ))
                            st.success("Schedule cancelled successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error cancelling schedule: {str(e)}")
        else:
            st.info("No scheduled documents found")
            
    # Processing Status Tab
    with tab3:
        st.header("Processing Status")
        if st.button("Refresh Status"):
            st.rerun()
            
        # Add processing status information here
        st.info("Processing status information will be displayed here")
        
    # Processed Documents Tab
    with tab4:
        st.header("Processed Documents")
        if st.button("Refresh Documents"):
            st.rerun()
            
        # Add processed documents information here
        st.info("Processed documents information will be displayed here")

if __name__ == "__main__":
    main()
