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

def fetch_catalogs():
    """Fetch catalog data from Siigo API"""
    try:
        if st.session_state.authenticated and st.session_state.api_client:
            st.session_state.cost_centers = st.session_state.api_client.get_cost_centers()
            st.session_state.document_types = st.session_state.api_client.get_document_types()
            error_logger.log_info("Successfully fetched catalog data")
    except Exception as e:
        error_logger.log_error(
            'api_errors',
            f"Error fetching catalogs: {str(e)}"
        )
        st.error(f"Error fetching catalogs: {str(e)}")

def get_task_status_color(next_run):
    """Get status color based on next run time"""
    try:
        next_run_dt = datetime.strptime(next_run, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        if next_run_dt < now:
            return "🔴 Overdue"
        elif (next_run_dt - now).total_seconds() < 3600:  # Within next hour
            return "🟡 Soon"
        else:
            return "🟢 Scheduled"
    except:
        return "⚪ Unknown"

def logout():
    """Logout user and clear session state"""
    st.session_state.authenticated = False
    st.session_state.api_client = None
    st.session_state.cost_centers = None
    st.session_state.document_types = None
    st.session_state.processing_results = []
    st.session_state.current_batch = None
    st.session_state.selected_task = None
    error_logger.log_info('User logged out successfully')
    st.rerun()

def process_entries(df):
    """Process journal entries from DataFrame"""
    results = []
    if st.session_state.authenticated and st.session_state.api_client:
        processor = ExcelProcessor(None)  # Just for API formatting
        for doc_id, group in df.groupby('document_id'):
            try:
                payload = processor.format_entries_for_api(group)
                response = st.session_state.api_client.create_journal_entry(payload)
                results.append({
                    'document_id': doc_id,
                    'date': group['date'].iloc[0],
                    'status': 'Success',
                    'message': 'Journal entry created successfully'
                })
            except Exception as e:
                results.append({
                    'document_id': doc_id,
                    'date': group['date'].iloc[0],
                    'status': 'Error',
                    'message': str(e)
                })
    return results

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
                    
                # Display last error details from log
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
        tab1, tab2, tab3, tab4 = st.tabs([
            "Journal Entry Processing",
            "Catalog Lookup",
            "Export Results",
            "Processing Status"
        ])

        # Journal Entry Processing Tab
        with tab1:
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
                            
                            # Display results
                            success_count = sum(1 for r in results if r['status'] == 'Success')
                            error_count = len(results) - success_count
                            
                            st.success(f"Processing completed: {success_count} successful, {error_count} failed")
                            if error_count > 0:
                                st.error("Some entries failed to process. Check the Export tab for details.")
                            
                            st.dataframe(pd.DataFrame(results))
                
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
                frequency = st.selectbox(
                    "Select frequency",
                    options=['daily', 'weekly', 'monthly'],
                    help="How often to process the journal entries"
                )
                
                day_of_week = None
                day_of_month = None
                
                if frequency == 'weekly':
                    day_of_week = st.selectbox(
                        "Select day of week",
                        options=list(range(7)),
                        format_func=lambda x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][x],
                        help="Day of the week to process entries"
                    )
                elif frequency == 'monthly':
                    day_of_month = st.number_input(
                        "Select day of month",
                        min_value=1,
                        max_value=31,
                        value=1,
                        help="Day of the month to process entries"
                    )
                
                schedule_file = st.file_uploader("Upload Excel file for scheduling", type=['xlsx', 'xls'])
                schedule_submit = st.form_submit_button("Schedule Processing")
                
                if schedule_submit and schedule_file:
                    try:
                        scheduler = TaskScheduler()
                        schedule_info = scheduler.schedule_task(
                            schedule_time,
                            schedule_file,
                            frequency=frequency,
                            day_of_week=day_of_week,
                            day_of_month=day_of_month
                        )
                        
                        frequency_text = f"{frequency} at {schedule_time}"
                        if frequency == 'weekly':
                            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                            frequency_text = f"{frequency} on {days[day_of_week]} at {schedule_time}"
                        elif frequency == 'monthly':
                            frequency_text = f"{frequency} on day {day_of_month} at {schedule_time}"
                            
                        error_logger.log_info(
                            f"Processing scheduled {frequency_text} with file {schedule_file.name}"
                        )
                        st.success(f"Processing scheduled {frequency_text}")
                    except Exception as e:
                        error_logger.log_error(
                            'processing_errors',
                            str(e),
                            {
                                'schedule_time': str(schedule_time),
                                'frequency': frequency,
                                'filename': schedule_file.name
                            }
                        )
                        st.error(f"Error scheduling task: {str(e)}")

        # Catalog Lookup Tab
        with tab2:
            st.header("Catalog Lookup")
            
            if st.button("Refresh Catalogs"):
                fetch_catalogs()

            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Cost Centers")
                if st.session_state.cost_centers:
                    cost_centers_df = pd.DataFrame(st.session_state.cost_centers)
                    if not cost_centers_df.empty:
                        search_cost = st.text_input("Search Cost Centers", key="cost_search")
                        filtered_cost = cost_centers_df
                        if search_cost:
                            filtered_cost = cost_centers_df[
                                cost_centers_df.apply(lambda x: x.astype(str).str.contains(search_cost, case=False).any(), axis=1)
                            ]
                        st.dataframe(filtered_cost, use_container_width=True)
                    else:
                        st.info("No cost centers available")
                else:
                    st.info("Cost centers not loaded")

            with col2:
                st.subheader("Document Types")
                if st.session_state.document_types:
                    doc_types_df = pd.DataFrame(st.session_state.document_types)
                    if not doc_types_df.empty:
                        search_doc = st.text_input("Search Document Types", key="doc_search")
                        filtered_doc = doc_types_df
                        if search_doc:
                            filtered_doc = doc_types_df[
                                doc_types_df.apply(lambda x: x.astype(str).str.contains(search_doc, case=False).any(), axis=1)
                            ]
                        st.dataframe(filtered_doc, use_container_width=True)
                    else:
                        st.info("No document types available")
                else:
                    st.info("Document types not loaded")

        # Export Tab
        with tab3:
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

        # Processing Status Tab
        with tab4:
            st.header("Scheduled Documents")
            
            # Overview metrics
            col1, col2, col3 = st.columns(3)
            scheduler = TaskScheduler()
            
            # Get tasks asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = loop.run_until_complete(scheduler.get_scheduled_tasks())
            
            with col1:
                total_tasks = len(tasks)
                st.metric("Total Scheduled Tasks", total_tasks)
            
            with col2:
                active_tasks = sum(1 for task in tasks if get_task_status_color(task['next_run']).startswith('🟢'))
                st.metric("Active Tasks", active_tasks)
            
            with col3:
                overdue_tasks = sum(1 for task in tasks if get_task_status_color(task['next_run']).startswith('🔴'))
                st.metric("Overdue Tasks", overdue_tasks)
            
            # Date range filter
            st.subheader("History Filter")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
            with col2:
                end_date = st.date_input("End Date", value=datetime.now())
                
            # Task filtering
            st.subheader("Task Management")
            col1, col2 = st.columns(2)
            
            with col1:
                status_filter = st.multiselect(
                    "Filter by Status",
                    ["🟢 Scheduled", "🟡 Soon", "🔴 Overdue"],
                    default=["🟢 Scheduled", "🟡 Soon", "🔴 Overdue"]
                )
            
            with col2:
                frequency_filter = st.multiselect(
                    "Filter by Frequency",
                    ["Daily", "Weekly", "Monthly"],
                    default=["Daily", "Weekly", "Monthly"]
                )
            
            # Display tasks
            if tasks:
                formatted_tasks = []
                for task in tasks:
                    task_history = loop.run_until_complete(
                        scheduler.get_task_history(
                            task['id'],
                            start_date.strftime('%Y-%m-%d'),
                            end_date.strftime('%Y-%m-%d')
                        )
                    )
                    
                    success_count = sum(1 for h in task_history if h['status'] == 'success')
                    failed_count = sum(1 for h in task_history if h['status'] == 'failed')
                    
                    formatted_task = {
                        "Status": get_task_status_color(task['next_run']),
                        "Next Run": task['next_run'],
                        "File": task['file_name'],
                        "Frequency": task['frequency'].title(),
                        "Success Rate": f"{(success_count / len(task_history) * 100):.1f}%" if task_history else "N/A",
                        "Last Run Status": task_history[0]['status'].title() if task_history else "N/A"
                    }
                    formatted_tasks.append(formatted_task)
                
                tasks_df = pd.DataFrame(formatted_tasks)
                
                # Apply filters
                filtered_df = tasks_df[
                    tasks_df['Status'].isin(status_filter) &
                    tasks_df['Frequency'].isin([f.title() for f in frequency_filter])
                ]
                
                if not filtered_df.empty:
                    st.dataframe(
                        filtered_df.style.apply(
                            lambda x: ['background-color: #ff4b4b' if '🔴' in str(val)
                                     else 'background-color: #ffeb3b' if '🟡' in str(val)
                                     else 'background-color: #4caf50' if '🟢' in str(val)
                                     else '' for val in x],
                            subset=['Status']
                        ).apply(
                            lambda x: ['background-color: #ff4b4b' if 'Failed' in str(val)
                                     else 'background-color: #4caf50' if 'Success' in str(val)
                                     else '' for val in x],
                            subset=['Last Run Status']
                        ),
                        use_container_width=True,
                        height=400
                    )
                    
                    # Task details view
                    st.subheader("Task Details")
                    selected_task_idx = st.selectbox(
                        "Select a task to view details",
                        options=filtered_df.index,
                        format_func=lambda x: f"{filtered_df.iloc[x]['File']} - {filtered_df.iloc[x]['Next Run']}"
                    )
                    
                    if selected_task_idx is not None:
                        task = filtered_df.iloc[selected_task_idx]
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### Schedule Information")
                            st.markdown(f"**Status:** {task['Status']}")
                            st.markdown(f"**Next Run:** {task['Next Run']}")
                            st.markdown(f"**Frequency:** {task['Frequency']}")
                            st.markdown(f"**Success Rate:** {task['Success Rate']}")
                            st.markdown(f"**Last Run Status:** {task['Last Run Status']}")
                        
                        with col2:
                            st.markdown("#### File Information")
                            st.markdown(f"**Filename:** {task['File']}")
                            
                            # Add action buttons
                            if st.button("Cancel Schedule", key=f"cancel_{selected_task_idx}"):
                                try:
                                    loop.run_until_complete(scheduler.cancel_task(selected_task_idx))
                                    st.success("Schedule canceled successfully")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error canceling schedule: {str(e)}")
                        
                        # Show task history
                        st.subheader("Execution History")
                        task_history = loop.run_until_complete(
                            scheduler.get_task_history(
                                selected_task_idx,
                                start_date.strftime('%Y-%m-%d'),
                                end_date.strftime('%Y-%m-%d')
                            )
                        )
                        
                        if task_history:
                            history_df = pd.DataFrame([{
                                'Run Time': h['run_time'],
                                'Status': h['status'].title(),
                                'Details': h['result'] if h['result'] else 'No details available'
                            } for h in task_history])
                            
                            st.dataframe(
                                history_df.style.apply(
                                    lambda x: ['background-color: #ff4b4b' if val == 'Failed'
                                             else 'background-color: #4caf50' if val == 'Success'
                                             else 'background-color: #ffeb3b' for val in x],
                                    subset=['Status']
                                ),
                                use_container_width=True
                            )
                        else:
                            st.info("No execution history available")
                else:
                    st.info("No tasks match the selected filters")
            else:
                st.info("No scheduled tasks available")

if __name__ == "__main__":
    main()
