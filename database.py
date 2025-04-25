
import os
import sqlite3

from typing import Optional, Dict, List, Union
from datetime import datetime

def get_db_connection() -> sqlite3.Connection:
    """Create and return a database connection with foreign key support"""
    conn = sqlite3.connect("smart_classroom.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS teacher_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            section_id INTEGER NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE,
            UNIQUE(teacher_id, section_id)
        );

        CREATE TABLE IF NOT EXISTS student_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            section_id INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE,
            UNIQUE(student_id, section_id)
        );

        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_data BLOB,      
            uploaded_by INTEGER NOT NULL,
            section_id INTEGER NOT NULL,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(uploaded_by) REFERENCES users(id),
            FOREIGN KEY(section_id) REFERENCES sections(id)
        );

        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            grade REAL NOT NULL,
            assignment_date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY(student_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATE NOT NULL,
            section_id INTEGER NOT NULL,
            max_grade REAL DEFAULT 100,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(section_id) REFERENCES sections(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(section_id) REFERENCES sections(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL,
            section_id INTEGER NOT NULL,
            created_by INTEGER NOT NULL,
            FOREIGN KEY(section_id) REFERENCES sections(id),
            FOREIGN KEY(created_by) REFERENCES users(id),
            UNIQUE(subject_name, section_id)
        );
        CREATE TABLE IF NOT EXISTS recommendation_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_name TEXT NOT NULL,
            section_id INTEGER NOT NULL,
            created_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(section_id) REFERENCES sections(id),
            FOREIGN KEY(created_by) REFERENCES users(id),
            UNIQUE(topic_name, section_id)
        );

        CREATE TABLE IF NOT EXISTS video_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            video_url TEXT NOT NULL,
            added_by INTEGER NOT NULL,
            title TEXT,  -- New column for video title
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(topic_id) REFERENCES recommendation_topics(id),
            FOREIGN KEY(added_by) REFERENCES users(id)
        );
        
        CREATE TABLE IF NOT EXISTS recommendation_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_name TEXT NOT NULL,
            section_id INTEGER NOT NULL,
            created_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(section_id) REFERENCES sections(id),
            FOREIGN KEY(created_by) REFERENCES users(id),
            UNIQUE(topic_name, section_id)
        );               

    """)

    # Create default admin
    default_admin = {
        "username": "admin",
        "password": "admin123",
        "role": "Admin"
    }
    cursor.execute("SELECT * FROM users WHERE username = ?", (default_admin["username"],))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (default_admin["username"], default_admin["password"], default_admin["role"])
        )
    
    conn.commit()
    conn.close()

# ================== User Management ==================
def add_user(username: str, password: str, role: str) -> bool:
    """Add a new user to the database"""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username exists
    finally:
        conn.close()

def get_user(username: str) -> Optional[Dict]:
    """Get a user by username"""
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users() -> List[Dict]:
    """Get all users from the database"""
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return [dict(user) for user in users]

# ================== Section Management ==================
def add_section(section_name: str) -> bool:
    """Add a new section to the database"""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO sections (section_name) VALUES (?)",
            (section_name,)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Section exists
    finally:
        conn.close()

def get_all_sections() -> List[Dict]:
    """Get all sections from the database"""
    conn = get_db_connection()
    sections = conn.execute("SELECT * FROM sections").fetchall()
    conn.close()
    return [dict(section) for section in sections]

def assign_section_to_teacher(teacher_id: int, section_id: int) -> bool:
    """Assign a section to a teacher"""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO teacher_sections (teacher_id, section_id) VALUES (?, ?)",
            (teacher_id, section_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Assignment exists
    finally:
        conn.close()

def assign_section_to_student(student_id: int, section_id: int) -> bool:
    """Assign a section to a student"""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO student_sections (student_id, section_id) VALUES (?, ?)",
            (student_id, section_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Assignment exists
    finally:
        conn.close()

def get_users_with_sections():
    """Get all users with their section assignments"""
    conn = get_db_connection()
    
    students = conn.execute("""
        SELECT u.id, u.username, s.section_name
        FROM users u
        LEFT JOIN student_sections ss ON u.id = ss.student_id
        LEFT JOIN sections s ON ss.section_id = s.id
        WHERE u.role = 'Student'
    """).fetchall()

    teachers = conn.execute("""
        SELECT u.id, u.username, s.section_name
        FROM users u
        LEFT JOIN teacher_sections ts ON u.id = ts.teacher_id
        LEFT JOIN sections s ON ts.section_id = s.id
        WHERE u.role = 'Teacher'
    """).fetchall()

    conn.close()
    return [dict(s) for s in students], [dict(t) for t in teachers]

def get_db_connection():
    """Establish connection to the SQLite database."""
    conn = sqlite3.connect("smart_classroom.db")
    conn.row_factory = sqlite3.Row
    return conn

def delete_user(user_id):
    """Delete a user and remove their associated records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Remove user from student_sections or teacher_sections first to prevent foreign key errors
        cursor.execute("DELETE FROM student_sections WHERE student_id = ?", (user_id,))
        cursor.execute("DELETE FROM teacher_sections WHERE teacher_id = ?", (user_id,))
        
        # Now, delete the user from the users table
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return True  # Deletion successful
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error deleting user: {e}")
        return False  

# ================== File Management ==================
def add_file(filename: str, file_type: str, file_data: bytes, uploaded_by: int, section_id: int) -> bool:
    """Add a file record with binary data to the database"""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO files 
            (filename, file_type, file_data, uploaded_by, section_id, uploaded_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))""",
            (filename, file_type, file_data, uploaded_by, section_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()



def get_files_by_type(file_type: str) -> List[Dict]:
    """Get files filtered by type"""
    conn = get_db_connection()
    files = conn.execute(
        "SELECT * FROM files WHERE file_type = ? ORDER BY uploaded_at DESC",
        (file_type,)
    ).fetchall()
    conn.close()
    return [dict(file) for file in files]

def get_teacher_sections(teacher_id: int) -> List[Dict]:
    """Get sections assigned to a teacher"""
    conn = get_db_connection()
    sections = conn.execute("""
        SELECT s.id, s.section_name 
        FROM teacher_sections ts
        JOIN sections s ON ts.section_id = s.id
        WHERE ts.teacher_id = ?
    """, (teacher_id,)).fetchall()
    conn.close()
    return [dict(section) for section in sections]

def get_student_files(student_id: int) -> List[Dict]:
    """Get files available to a student"""
    conn = get_db_connection()
    files = conn.execute("""
        SELECT f.*, s.section_name 
        FROM files f
        JOIN student_sections ss ON f.section_id = ss.section_id
        JOIN sections s ON f.section_id = s.id
        WHERE ss.student_id = ?
    """, (student_id,)).fetchall()
    conn.close()
    return [dict(file) for file in files]

# ================== Grade Management ==================
def add_grade(student_id: int, subject: str, grade: float) -> bool:
    """Add a new grade entry"""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO grades (student_id, subject, grade) VALUES (?, ?, ?)",
            (student_id, subject, grade)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Grade insertion error: {e}")
        return False
    finally:
        conn.close()

def get_student_grades(student_id: int) -> List[Dict]:
    """Get all grades for a student"""
    conn = get_db_connection()
    grades = conn.execute(
        "SELECT subject, grade, assignment_date FROM grades WHERE student_id = ?",
        (student_id,)
    ).fetchall()
    conn.close()
    return [dict(grade) for grade in grades]

def update_grade(grade_id: int, new_grade: float) -> bool:
    """Update an existing grade"""
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE grades SET grade = ? WHERE id = ?",
            (new_grade, grade_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Grade update error: {e}")
        return False
    finally:
        conn.close()

def delete_grade(grade_id: int) -> bool:
    """Delete a grade entry"""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Grade deletion error: {e}")
        return False
    finally:
        conn.close()

# ================== Assignment Management ==================
def create_assignment(title: str, description: str, due_date: str, section_id: int) -> bool:
    """Create a new assignment"""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO assignments 
            (title, description, due_date, section_id) 
            VALUES (?, ?, ?, ?)""",
            (title, description, due_date, section_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Assignment creation error: {e}")
        return False
    finally:
        conn.close()

def get_assignments_by_section(section_id: int) -> List[Dict]:
    """Get assignments for a section"""
    conn = get_db_connection()
    assignments = conn.execute(
        "SELECT * FROM assignments WHERE section_id = ?",
        (section_id,)
    ).fetchall()
    conn.close()
    return [dict(assignment) for assignment in assignments]

def get_section_files(section_id: int, file_type: str = None) -> List[Dict]:
    """Get files for a specific section"""
    conn = get_db_connection()
    query = "SELECT * FROM files WHERE section_id = ?"
    params = [section_id]
    
    if file_type:
        query += " AND file_type = ?"
        params.append(file_type)
        
    files = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(file) for file in files]

def delete_file(file_id: int, user_id: int) -> bool:
    """Delete a file if user is the uploader"""
    conn = get_db_connection()
    try:
        file_info = conn.execute(
            "SELECT file_path, uploaded_by FROM files WHERE id = ?",
            (file_id,)
        ).fetchone()
        
        if not file_info or file_info['uploaded_by'] != user_id:
            return False
            
        if os.path.exists(file_info['file_path']):
            os.remove(file_info['file_path'])
            
        conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Delete error: {e}")
        return False
    finally:
        conn.close()

# ================== Chat Functionality ==================
def save_message(section_id: int, user_id: int, content: str) -> bool:
    """Save a chat message to the database"""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO messages (section_id, user_id, content) VALUES (?, ?, ?)",
            (section_id, user_id, content)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False
    finally:
        conn.close()

def get_messages(section_id: int) -> List[Dict]:
    """Retrieve messages for a section"""
    conn = get_db_connection()
    messages = conn.execute("""
        SELECT m.*, u.username, u.role 
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE section_id = ?
        ORDER BY timestamp ASC
    """, (section_id,)).fetchall()
    conn.close()
    return [dict(msg) for msg in messages]

def delete_message(message_id: int, user_id: int, user_role: str) -> bool:
    """Delete a message from the chat"""
    conn = get_db_connection()
    try:
        if user_role == "Teacher":
            conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        else:
            conn.execute("DELETE FROM messages WHERE id = ? AND user_id = ?", 
                        (message_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Delete error: {e}")
        return False
    finally:
        conn.close()

def get_student_sections(student_id: int) -> List[Dict]:
    """Get sections assigned to a student"""
    conn = get_db_connection()
    sections = conn.execute("""
        SELECT s.id, s.section_name 
        FROM student_sections ss
        JOIN sections s ON ss.section_id = s.id
        WHERE ss.student_id = ?
    """, (student_id,)).fetchall()
    conn.close()
    return [dict(section) for section in sections]

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")

    # database.py - Add these new functions

def get_teacher_section_students(teacher_id: int) -> List[Dict]:
    """Get all students in sections taught by a teacher"""
    conn = get_db_connection()
    students = conn.execute("""
        SELECT DISTINCT u.id, u.username, s.section_name
        FROM users u
        JOIN student_sections ss ON u.id = ss.student_id
        JOIN teacher_sections ts ON ss.section_id = ts.section_id
        JOIN sections s ON ts.section_id = s.id
        WHERE ts.teacher_id = ?
    """, (teacher_id,)).fetchall()
    conn.close()
    return [dict(row) for row in students]

def get_student_subject_grades(student_id: int) -> Dict[str, List[float]]:
    """Get all grades for a student grouped by subject"""
    conn = get_db_connection()
    grades = conn.execute("""
        SELECT subject, grade 
        FROM grades 
        WHERE student_id = ?
    """, (student_id,)).fetchall()
    conn.close()
    
    subject_grades = {}
    for row in grades:
        subject = row['subject']
        subject_grades.setdefault(subject, []).append(row['grade'])
    return subject_grades

# database.py - Add these in the Grade Management section

def get_students_by_section(section_id: int) -> List[Dict]:
    """Get all students in a specific section"""
    conn = get_db_connection()
    students = conn.execute("""
        SELECT u.id, u.username 
        FROM users u
        JOIN student_sections ss ON u.id = ss.student_id
        WHERE ss.section_id = ?
    """, (section_id,)).fetchall()
    conn.close()
    return [dict(student) for student in students]

def get_section_grades(section_id: int) -> List[Dict]:
    """Get all grades for a section"""
    conn = get_db_connection()
    grades = conn.execute("""
        SELECT g.*, u.username 
        FROM grades g
        JOIN users u ON g.student_id = u.id
        WHERE u.id IN (
            SELECT student_id FROM student_sections WHERE section_id = ?
        )
    """, (section_id,)).fetchall()
    conn.close()
    return [dict(grade) for grade in grades]

# database.py - Add these in the Grade Management section

def get_students_by_section(section_id: int) -> List[Dict]:
    """Get all students in a specific section"""
    conn = get_db_connection()
    students = conn.execute("""
        SELECT u.id, u.username 
        FROM users u
        JOIN student_sections ss ON u.id = ss.student_id
        WHERE ss.section_id = ?
    """, (section_id,)).fetchall()
    conn.close()
    return [dict(student) for student in students]

def get_section_grades(section_id: int) -> List[Dict]:
    """Get all grades for a section"""
    conn = get_db_connection()
    grades = conn.execute("""
        SELECT g.*, u.username 
        FROM grades g
        JOIN users u ON g.student_id = u.id
        WHERE u.id IN (
            SELECT student_id FROM student_sections WHERE section_id = ?
        )
    """, (section_id,)).fetchall()
    conn.close()
    return [dict(grade) for grade in grades]

def create_subject(subject_name: str, section_id: int, teacher_id: int) -> bool:
    """Create a new subject for a section"""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO subjects (subject_name, section_id, created_by) VALUES (?, ?, ?)",
            (subject_name, section_id, teacher_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Subject already exists in section
    finally:
        conn.close()

def get_section_subjects(section_id: int) -> List[Dict]:
    """Get all subjects for a section"""
    conn = get_db_connection()
    subjects = conn.execute(
        "SELECT id, subject_name FROM subjects WHERE section_id = ?",
        (section_id,)
    ).fetchall()
    conn.close()
    return [dict(subject) for subject in subjects]

def delete_subject(subject_id: int, teacher_id: int) -> bool:
    """Delete a subject if created by the teacher"""
    conn = get_db_connection()
    try:
        conn.execute(
            "DELETE FROM subjects WHERE id = ? AND created_by = ?",
            (subject_id, teacher_id)
        )
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()

# Add to database.py

def create_topic(topic_name: str, section_id: int, created_by: int) -> bool:
    """Create a new recommendation topic"""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO recommendation_topics 
            (topic_name, section_id, created_by) 
            VALUES (?, ?, ?)""",
            (topic_name.strip(), section_id, created_by)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Topic already exists
    finally:
        conn.close()

def get_section_topics(section_id: int) -> List[Dict]:
    """Get all topics for a section"""
    conn = get_db_connection()
    topics = conn.execute(
        """SELECT t.id, t.topic_name, u.username as created_by 
        FROM recommendation_topics t
        JOIN users u ON t.created_by = u.id
        WHERE section_id = ?""",
        (section_id,)
    ).fetchall()
    conn.close()
    return [dict(topic) for topic in topics]

def add_video_recommendation(topic_id: int, video_url: str, student_id: int, title: str) -> bool:
    """Add a video recommendation to a topic"""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO video_recommendations 
            (topic_id, video_url, added_by, title) 
            VALUES (?, ?, ?, ?)""",
            (topic_id, video_url.strip(), student_id, title)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def get_topic_recommendations(topic_id: int) -> List[Dict]:
    """Get all recommendations for a topic"""
    conn = get_db_connection()
    recommendations = conn.execute(
        """SELECT v.id, v.video_url, u.username as added_by 
        FROM video_recommendations v
        JOIN users u ON v.added_by = u.id
        WHERE topic_id = ?""",
        (topic_id,)
    ).fetchall()
    conn.close()
    return [dict(rec) for rec in recommendations]
# Add to database.py

# ================== YouTube Recommendations ==================
def create_topic(topic_name: str, section_id: int, created_by: int) -> bool:
    """Create a new recommendation topic"""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO recommendation_topics 
            (topic_name, section_id, created_by) 
            VALUES (?, ?, ?)""",
            (topic_name.strip(), section_id, created_by)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Topic already exists
    finally:
        conn.close()

def get_section_topics(section_id: int) -> List[Dict]:
    """Get all topics for a section"""
    conn = get_db_connection()
    topics = conn.execute(
        """SELECT t.id, t.topic_name, u.username as created_by 
        FROM recommendation_topics t
        JOIN users u ON t.created_by = u.id
        WHERE section_id = ?""",
        (section_id,)
    ).fetchall()
    conn.close()
    return [dict(topic) for topic in topics]

def add_video_recommendation(topic_id: int, video_url: str, student_id: int, title: str) -> bool:
    """Add a video recommendation to a topic"""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO video_recommendations 
            (topic_id, video_url, added_by, title) 
            VALUES (?, ?, ?, ?)""",
            (topic_id, video_url.strip(), student_id, title)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def get_topic_recommendations(topic_id: int) -> List[Dict]:
    """Get all recommendations for a topic"""
    conn = get_db_connection()
    recommendations = conn.execute(
        """SELECT v.id, v.video_url, v.title, u.username as added_by 
        FROM video_recommendations v
        JOIN users u ON v.added_by = u.id
        WHERE topic_id = ?""",
        (topic_id,)
    ).fetchall()
    conn.close()
    return [dict(rec) for rec in recommendations]

# Add these table creations to init_db() function
def get_student_section_files(student_id: int, file_type: str = None) -> List[Dict]:
    """Get all PDFs or videos for the student's assigned sections"""
    conn = get_db_connection()
    query = """
        SELECT f.filename, f.file_path, f.uploaded_at
        FROM files f
        JOIN student_sections ss ON f.section_id = ss.section_id
        WHERE ss.student_id = ?
    """
    params = [student_id]
    
    if file_type:
        query += " AND f.file_type = ?"
        params.append(file_type)
    
    files = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(file) for file in files]
