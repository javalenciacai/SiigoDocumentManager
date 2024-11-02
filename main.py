# Previous imports remain the same...
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
if 'date_filter' not in st.session_state:
    st.session_state.date_filter = 'all'

# Previous functions remain the same...

def main():
    st.title("Siigo Journal Entry Processor")
    
    # Sidebar content remains the same...
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
    
    # Authentication section remains the same...
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
            "Processed Documents"  # New tab
        ])

        # Previous tabs remain the same...
        # Add new tab for processed documents
        with tab5:
            st.header("Processed Documents")
            
            # Date filter
            filter_col1, filter_col2 = st.columns([2, 2])
            with filter_col1:
                st.session_state.date_filter = st.selectbox(
                    "Filter by date",
                    options=['all', 'today', 'this_week', 'this_month', 'custom'],
                    help="Filter processed documents by date range"
                )
            
            start_date = None
            end_date = None
            
            if st.session_state.date_filter == 'custom':
                with filter_col2:
                    col1, col2 = st.columns(2)
                    with col1:
                        start_date = st.date_input("Start date")
                    with col2:
                        end_date = st.date_input("End date")
            elif st.session_state.date_filter == 'today':
                start_date = datetime.now().date()
                end_date = start_date
            elif st.session_state.date_filter == 'this_week':
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=end_date.weekday())
            elif st.session_state.date_filter == 'this_month':
                now = datetime.now()
                start_date = now.replace(day=1).date()
                end_date = now.date()
            
            # Filter results based on date range
            filtered_results = st.session_state.processing_results
            if start_date and end_date:
                filtered_results = [
                    result for result in filtered_results
                    if start_date <= datetime.strptime(result['date'], '%Y-%m-%d').date() <= end_date
                ]
            
            # Display results in tabs based on status
            if filtered_results:
                success_results = [r for r in filtered_results if r['status'] == 'Success']
                error_results = [r for r in filtered_results if r['status'] == 'Error']
                
                result_tabs = st.tabs(["All", "Successful", "Failed"])
                
                with result_tabs[0]:
                    if filtered_results:
                        st.dataframe(
                            pd.DataFrame(filtered_results).sort_values('date', ascending=False),
                            use_container_width=True
                        )
                    else:
                        st.info("No documents processed in selected date range")
                
                with result_tabs[1]:
                    if success_results:
                        st.dataframe(
                            pd.DataFrame(success_results).sort_values('date', ascending=False),
                            use_container_width=True
                        )
                    else:
                        st.info("No successful documents in selected date range")
                
                with result_tabs[2]:
                    if error_results:
                        st.dataframe(
                            pd.DataFrame(error_results).sort_values('date', ascending=False),
                            use_container_width=True
                        )
                    else:
                        st.info("No failed documents in selected date range")
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Documents", len(filtered_results))
                with col2:
                    st.metric("Successful", len(success_results))
                with col3:
                    st.metric("Failed", len(error_results))
                
                # Export filtered results
                if st.button("Export Filtered Results"):
                    output = export_to_excel(
                        filtered_results,
                        "filtered_results.xlsx"
                    )
                    st.download_button(
                        label="Download Filtered Results",
                        data=output,
                        file_name="filtered_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info("No documents processed yet")

if __name__ == "__main__":
    main()
