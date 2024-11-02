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

        # Rest of the tabs remain the same...

if __name__ == "__main__":
    main()
