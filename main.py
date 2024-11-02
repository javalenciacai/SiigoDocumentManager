# Previous imports remain the same...
[Previous content until line 248]

                        st.info(f"Next scheduled run will be at: {next_run.strftime('%Y-%m-%d %H:%M')}")
                        
                        # Schedule button with confirmation
                        if st.button("Schedule Processing", type="primary"):
                            try:
                                scheduler = TaskScheduler()
                                task_data = scheduler.schedule_task(schedule_time, uploaded_file, frequency, **schedule_params)
                                
                                # Success message with details
                                st.success("✅ Task scheduled successfully!")
                                
                                # Show schedule details in a formatted box
                                st.markdown("### 📋 Schedule Details")
                                details = {
                                    "📁 File": uploaded_file.name,
                                    "🔄 Frequency": frequency.capitalize(),
                                    "⏰ Time": schedule_time.strftime("%H:%M"),
                                    "📅 Next Run": next_run.strftime("%Y-%m-%d %H:%M")
                                }
                                if frequency == "weekly":
                                    details["📆 Day"] = days[schedule_params['day_of_week']]
                                elif frequency == "monthly":
                                    details["📆 Day"] = f"{schedule_params['day_of_month']}th"
                                
                                # Display details in a clean format
                                for key, value in details.items():
                                    st.markdown(f"**{key}:** {value}")
                                
                                # Add direct link to Processing Status tab
                                st.info("🔍 View and manage all scheduled tasks in the **Processing Status** tab")
                                if st.button("Go to Processing Status"):
                                    st.switch_page("Processing Status")
                                    
                            except Exception as e:
                                st.error(f"❌ Error scheduling task: {str(e)}")
                                error_logger.log_error(
                                    'processing_errors',
                                    f"Error scheduling task: {str(e)}"
                                )

[Rest of the file remains the same...]
