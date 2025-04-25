import streamlit as st
import pandas as pd
from database import get_db_connection

def student_dashboard():
    """Main student dashboard interface"""
    st.header("🎓 Student Dashboard")
    
    # Get student information
    student_id = st.session_state.user_id
    
    # Get enrolled sections
    conn = get_db_connection()
    sections = conn.execute(
        """
        SELECT s.section_name 
        FROM student_sections ss
        JOIN sections s ON ss.section_id = s.id
        WHERE ss.student_id = ?
        """,
        (student_id,)
    ).fetchall()
    
    # Get performance data
    grades = conn.execute(
        "SELECT subject, grade FROM grades WHERE student_id = ?",
        (student_id,)
    ).fetchall()
    
    conn.close()

    # Display sections
    if sections:
        st.subheader("📚 Enrolled Sections")
        for section in sections:
            st.write(f"- **{section['section_name']}**")
    else:
        st.info("No enrolled sections yet.")

    # Display academic performance
    if grades:
        st.subheader("📊 Academic Performance")
        grades_df = pd.DataFrame([dict(g) for g in grades])
        st.bar_chart(grades_df.set_index("subject"))
    else:
        st.info("No grade information available yet.")
