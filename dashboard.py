import os
import pandas as pd
import streamlit as st
from typing import List, Dict  # Add this line

from datetime import datetime
from database import (
    add_grade,
    delete_file,
    delete_message,
    get_messages,
    get_section_files,
    get_section_grades,
    get_students_by_section,
    get_teacher_sections,
    add_file,
    get_db_connection,
    save_message,
    get_section_subjects, 
    create_subject,       
    delete_subject  
)

def teacher_dashboard():
    """Main teacher dashboard interface"""
    st.header("👩🏫 Teacher Dashboard")
    st.write(f"Welcome, {st.session_state.username}!")
    
    # Display assigned sections
    teacher_id = st.session_state.user_id
    sections = get_teacher_sections(teacher_id)
    
    if sections:
        st.subheader("Your Assigned Sections")
        cols = st.columns(3)
        for idx, section in enumerate(sections):
            with cols[idx % 3]:
                st.markdown(f"""
                **{section['section_name']}**  
                *Section ID: {section['id']}*
                """)
    else:
        st.warning("You are not assigned to any sections yet.")



def upload_pdfs():
    """PDF upload functionality with section selection"""
    st.header("📄 Upload Course Materials")
    
    teacher_id = st.session_state.user_id
    sections = get_teacher_sections(teacher_id)

    if not sections:
        st.warning("No sections assigned. Contact administrator.")
        return

    selected_section = st.selectbox(
        "Select Target Section",
        options=[(s['id'], s['section_name']) for s in sections],
        format_func=lambda x: x[1]
    )

    uploaded_file = st.file_uploader("Choose PDF file", type=["pdf"])

    if uploaded_file and selected_section:
        if st.button("Confirm Upload"):
            file_data = uploaded_file.read()  # Read file as binary
            original_name = uploaded_file.name.replace(" ", "_").lower()

            if add_file(
                filename=original_name,
                file_type="pdf",
                 # No need for file path, saving as BLOB
                uploaded_by=teacher_id,
                section_id=selected_section[0],
                file_data = uploaded_file.read()  # Read file as binary content
            ):
                st.success(f"✅ Uploaded successfully to {selected_section[1]} section!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed to save file record")

def upload_videos():
    """Video upload functionality with section selection"""
    st.header("🎥 Upload Lecture Videos")

    teacher_id = st.session_state.user_id
    sections = get_teacher_sections(teacher_id)

    if not sections:
        st.warning("No sections assigned. Contact administrator.")
        return

    selected_section = st.selectbox(
        "Select Target Section",
        options=[(s['id'], s['section_name']) for s in sections],
        format_func=lambda x: x[1],
        key="video_section"
    )

    uploaded_video = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi", "mkv"])

    if uploaded_video and selected_section:
        if st.button("Confirm Upload"):
            file_data = uploaded_video.read()  # Read file as binary
            original_name = uploaded_video.name.replace(" ", "_").lower()

            if add_file(
                filename=original_name,
                file_type="video",
                  # No need for file path, saving as BLOB
                uploaded_by=teacher_id,
                section_id=selected_section[0],
                file_data = uploaded_video.read()# Read file as binary content
            ):
                st.success(f"✅ Uploaded successfully to {selected_section[1]} section!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed to save video record")
def class_chat():
    """Persistent class chat component"""
    st.header("💬 Class Chat")
    
    if "selected_section" not in st.session_state:
        st.error("Select a section first")
        return
    
    section_id = st.session_state.selected_section[0]
    user_id = st.session_state.user_id
    
    with st.container(height=500):
        messages = get_messages(section_id)
        for msg in messages:
            with st.chat_message("teacher" if msg['role'] == "Teacher" else "user"):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{msg['username']}**  \n{msg['content']}")
                with col2:
                    st.caption(msg['timestamp'].split()[0])
                    if st.session_state.role == "Teacher":
                        if st.button("🗑️", key=f"del_msg_{msg['id']}"):
                            delete_message(msg['id'], "Teacher")
                            st.rerun()
    
    if prompt := st.chat_input("Type your message..."):
        save_message(section_id, user_id, prompt)
        st.rerun()

# teacher/dashboard.py - Add this new function

def grade_management():
    """Interface for managing student grades"""
    st.subheader("📝 Grade Management")
    
    teacher_id = st.session_state.user_id
    sections = get_teacher_sections(teacher_id)
    
    if not sections:
        st.warning("No sections assigned")
        return
    
    # Section selection
    selected_section = st.selectbox(
        "Select Section",
        options=[(s['id'], s['section_name']) for s in sections],
        format_func=lambda x: x[1],
        key="grade_section"
    )
    
    # Student and subject inputs
    students = get_students_by_section(selected_section[0])
    subjects = ["Math", "Science", "History", "English", "Computer Science"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        student = st.selectbox("Student", students, format_func=lambda x: x['username'])
    with col2:
        subject = st.selectbox("Subject", subjects)
    with col3:
        grade = st.number_input("Grade (%)", min_value=0, max_value=100, step=1)
    
    if st.button("Record Grade"):
        if add_grade(student['id'], subject, grade):
            st.success("Grade recorded successfully!")
        else:
            st.error("Failed to record grade")
    
    # Display existing grades
    st.divider()
    st.subheader("Existing Grades")
    grades = get_section_grades(selected_section[0])
    
    if grades:
        df = pd.DataFrame(grades)
        df['assignment_date'] = pd.to_datetime(df['assignment_date'])
        st.dataframe(
            df[['username', 'subject', 'grade', 'assignment_date']],
            column_config={
                "grade": st.column_config.NumberColumn(format="%d %%"),
                "assignment_date": "Last Updated"
            },
            use_container_width=True
        )
    else:
        st.info("No grades recorded for this section")

# teacher/dashboard.py - Add this new function
from database import (
    get_teacher_sections, 
    get_students_by_section,  # Add this import
    add_grade, 
    get_section_grades  # Add this import
)

def grade_management():
    """Interface for teachers to add/view grades and manage subjects"""
    st.header("📝 Grade Management")
    
    if st.session_state.role != "Teacher":
        st.error("This page is only accessible to teachers")
        return
    
    teacher_id = st.session_state.user_id
    sections = get_teacher_sections(teacher_id)
    
    if not sections:
        st.warning("You are not assigned to any sections yet")
        return
    
    # Section Selection
    selected_section = st.selectbox(
        "Select Section",
        options=[(s['id'], s['section_name']) for s in sections],
        format_func=lambda x: x[1],
        key="grade_section"
    )
    section_id = selected_section[0]
    
    # Subject Management
    with st.expander("📚 Manage Subjects", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_subject = st.text_input("Add New Subject", key="new_subject")
        with col2:
            if st.button("➕ Add Subject"):
                if new_subject.strip():
                    if create_subject(new_subject.strip(), section_id, teacher_id):
                        st.success("Subject added!")
                        st.rerun()
                    else:
                        st.error("Subject already exists in this section!")
                
        # Display existing subjects
        subjects = get_section_subjects(section_id)
        if subjects:
            st.write("Existing Subjects:")
            cols = st.columns(4)
            for idx, subject in enumerate(subjects):
                with cols[idx % 4]:
                    with st.container(border=True):
                        st.markdown(f"**{subject['subject_name']}**")
                        if st.button("🗑️", key=f"del_sub_{subject['id']}"):
                            if delete_subject(subject['id'], teacher_id):
                                st.rerun()
    
    # Student Selection
    students = get_students_by_section(section_id)
    if not students:
        st.warning("No students in this section")
        return
    
    # Grade Input Section
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        student = st.selectbox(
            "Select Student",
            options=students,
            format_func=lambda x: x['username']
        )
    with col2:
        subjects = get_section_subjects(section_id)
        subject_options = [s['subject_name'] for s in subjects]
        subject = st.selectbox(
            "Subject",
            options=subject_options,
            disabled=not subjects
        )
    with col3:
        grade = st.number_input(
            "Grade (%)", 
            min_value=0, 
            max_value=100, 
            value=60
        )
    
    # Submit Button
    if st.button("Record Grade"):
        if not subjects:
            st.error("Please create subjects first!")
        else:
            if add_grade(student['id'], subject, grade):
                st.success("Grade recorded successfully!")
            else:
                st.error("Failed to record grade")
    
    # Existing Grades Table
    st.divider()
    st.subheader("Existing Grades")
    grades = get_section_grades(section_id)
    
    if grades:
        df = pd.DataFrame(grades)
        st.dataframe(
            df[['username', 'subject', 'grade', 'assignment_date']],
            column_config={
                "grade": st.column_config.NumberColumn(format="%d %%"),
                "assignment_date": "Last Updated"
            },
            use_container_width=True
        )
    else:
        st.info("No grades recorded for this section yet")
