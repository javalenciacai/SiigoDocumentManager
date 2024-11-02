# Previous content remains the same until line 295
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
# Rest of the file remains the same
