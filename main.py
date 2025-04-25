import streamlit as st
from auth import login, logout, authentication_guard
from database import init_db
from admin.dashboard import admin_dashboard
from teacher.dashboard import teacher_dashboard, upload_pdfs, upload_videos, class_chat, grade_management
from student.dashboard import student_dashboard
from features.study_materials import study_materials
from features.chatbot import chatbot
from features.roadmap import roadmap
from features.youtube_recommendations import youtube_recommendations
from features.mark_analysis import mark_analysis
from features.resume import resume_main
from features.course_recommendations import course_recommendations  # New import

# Initialize the database
init_db()

# Set Streamlit page configuration
st.set_page_config(
    page_title="EDUPORTFOLIO-Empowering Minds,Shaping Futures",
    page_icon="https://th.bing.com/th/id/OIP.TJP_NS2M8xCZQT5CW9vZ8gHaH_?w=162&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7",
    layout="wide",
    initial_sidebar_state="expanded"
)

def handle_navigation():
    """Manage role-based navigation and page routing"""
    NAV_CONFIG = {
        "Student": {
            "🏠 Dashboard": student_dashboard,
            "📚 Study Materials": study_materials,
            "💬 AI Assistant": chatbot,
            "🗺 Learning Path": roadmap,
            "🎥 Video Recommendations": youtube_recommendations,
            "📖 Course Recommendations": course_recommendations,
            "🤖 AI Interview Prep": resume_main
        },
        "Teacher": {
            "🏠 Dashboard": teacher_dashboard,
            "📝 Grade Management": grade_management,
            "📤 Upload PDFs": upload_pdfs,
            "🎬 Lecture Videos": upload_videos,
            "📊 Mark Analysis": mark_analysis,
        },
        "Admin": {
            "🏠 Dashboard": admin_dashboard,
            "👥 User Management": admin_dashboard,
            "📂 Section Management": admin_dashboard,
            "📊 Analytics": youtube_recommendations,
            "⚙ System Settings": roadmap
        }
    }

    if st.session_state.role not in NAV_CONFIG:
        st.error("Invalid role detected. Please log in again.")
        logout()
        return

    st.sidebar.title(f"{st.session_state.role} Portal")
    selected = st.sidebar.radio(
        "Main Menu",
        options=list(NAV_CONFIG[st.session_state.role].keys()),
        key='nav_selection'
    )

    try:
        NAV_CONFIG[st.session_state.role][selected]()
    except KeyError as e:
        st.error(f"Page configuration error: {str(e)}")
        logout()

    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", key="logout_btn"):
        logout()

def main():
    """Main application controller"""

    # Session state initialization
    required_keys = ['user_id', 'role', 'username', 'authenticated']
    for key in required_keys:
        st.session_state.setdefault(key, None)

    if not st.session_state.authenticated:
        login()
    else:
        authentication_guard()
        handle_navigation()

if __name__ == "__main__":
    main()
