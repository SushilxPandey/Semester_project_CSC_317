import sqlite3
import hashlib

# Database file path
DB_PATH = 'collegelife.db'

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
              id                INTEGER PRIMARY KEY AUTOINCREMENT,
              full_name         TEXT NOT NULL,
              email             TEXT NOT NULL UNIQUE,
              student_id        TEXT NOT NULL UNIQUE,
              password          TEXT NOT NULL
              )
              """)
    
    # Tasks table
    c.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
              id               INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id          INTEGER NOT NULL,
              title            TEXT NOT NULL,
              description      TEXT,
              due_date         TEXT,
              due_time         TEXT,
              priority         TEXT DEFAULT 'Medium',
              status           TEXT DEFAULT 'Pending',
              reminder         INTEGER DEFAULT 0,
              FOREIGN KEY (user_id) REFERENCES users (id)
              )
              """)
    
    #Events table
    c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                title            TEXT NOT NULL,
                description      TEXT,
                event_date       TEXT,
                event_time       TEXT,
                location         TEXT,
                category         TEXT DEFAULT 'Social',
                attending        INTEGER DEFAULT 0
              )
              """)
    # Settings table
    c.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                 user_id             INTEGER PRIMARY KEY,
                theme                TEXT DEFAULT 'Light',
                font_size            TEXT DEFAULT 'Medium',
                notifications        INTEGER DEFAULT 1,  
                FOREIGN KEY (user_id) REFERENCES users(id)
             )
             """)

    conn.commit()
    conn.close()

# Seeding some sample events
def seed_events():
    """Add sample events if table is empty"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM events")
    count = c.fetchone()[0]
    
    if count == 0:
        from datetime import datetime, timedelta
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Adding some sample events
        c.executemany("""
            INSERT INTO events (title, description, event_date, event_time, location, category, attending)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            ("Campus Club Fair", "Meet all campus clubs", today, "19:00", "Union", "Social", 143),
            ("AI Guest Lecture", "Open to all students", tomorrow, "14:00", "Auditorium B", "Academic", 17),
            ("Study Skills Workshop", "Academic success tips", next_week, "10:00", "Library", "Academic", 34),
            ("International Food Festival", "Food from 20+ countries", next_week, "12:00", "Student Center", "Social", 89),
        ])
        conn.commit()
    conn.close()



# __USER AUTHENTICATION___
def login_user(email, password):
    conn = get_connection()
    c = conn.cursor()

    hashed = hash_password(password)

    c.execute("""
            SELECT id, full_name, email, student_id
            FROM users
            WHERE email = ? AND password = ?
            """, (email, hashed))
    row = c.fetchone()
    conn.close()

    if row:
        return True, {
            'id': row[0],
            'full_name': row[1],
            'email': row[2],
            'student_id': row[3]
        }

    return False, "Invalid email or password."

def register_user(name, email, student_id, password):
    try:
        conn = get_connection()
        c = conn.cursor()

        hashed = hash_password(password)

        c.execute("""

            INSERT INTO users (full_name, email, student_id, password)  
            VALUES (?, ?, ?, ?)""", (name, email, student_id, hashed))
        
        user_id = c.lastrowid
        c.execute("INSERT INTO settings (user_id) VALUES (?)", (user_id,))  #creating default settings for the new user
        
        conn.commit()
        conn.close()

        return  True, "Account created successfully."

    except sqlite3.IntegrityError as e:
        if "email" in str(e):
            return False, "This email is already registered."
        elif "student_id" in str(e):
            return False, "This student ID is already registered."
        
        return False, "Registration failed. Try Again Later."


def get_task_stats(user_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
            SELECT COUNT(*) FROM tasks WHERE user_id = ?
            """, (user_id,))
    total = c.fetchone()[0]

    c.execute("""
            SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'Completed'
            """, (user_id,))
    done = c.fetchone()[0]

    conn.close()

    return total, done


def get_tasks(user_id, filter_type = 'all'):
    conn = get_connection()
    c = conn.cursor()

    #putting the tasks in order
    order = """
        ORDER BY
            CASE status
                WHEN 'Pending' THEN 0
                WHEN 'Completed' THEN 1
            END ASC,

            CASE WHEN due_date = '' OR due_date IS NULL THEN 1 ELSE 0 END,
            due_date ASC,

            CASE priority
                WHEN 'High'   THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low'    THEN 3
            END ASC
        """

    #filering tasks on today by getting the date of today
    if filter_type == 'today':
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute("""
            SELECT*FROM tasks
            WHERE user_id = ? AND due_date = ? AND status != 'Completed'
                  """ + order, (user_id, today))

    elif filter_type == 'week':
        from datetime import datetime, timedelta
        today = datetime.now().strftime('%Y-%m-%d')
        week = (datetime.now() + timedelta(days = 7)).strftime('%Y-%m-%d')
        c.execute("""
            SELECT*FROM tasks
            WHERE user_id = ? AND due_date BETWEEN ? AND ? AND status != 'Completed'   
                """ + order, (user_id, today, week))
    
    elif filter_type == 'done':
        c.execute ("""
            SELECT*FROM tasks 
            WHERE user_id = ? AND status = 'Completed'
            ORDER BY id DESC
                    """ , (user_id,))
    
    else:
        c.execute("SELECT*FROM tasks WHERE user_id  = ?" + order, (user_id,))

    tasks = c.fetchall()
    conn.close()
    return tasks

def mark_task_done(task_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE tasks SET status = 'Completed' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

#saving the new task
def add_task(user_id, title, description, due_date, due_time, priority, reminder):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (user_id, title, description, due_date, due_time, priority, reminder)
        VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, title, description, due_date, due_time, priority, int(reminder)))
    conn.commit()
    conn.close()

#marker to remove the completed status   
def mark_task_pending(task_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("UPDATE tasks SET status = 'Pending' WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()

def get_overdue_tasks(user_id):
    conn = get_connection()
    c = conn.cursor()
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("""
            SELECT*FROM tasks
            WHERE user_id = ? AND due_date < ? AND due_date!= '' AND status != 'Completed'
            ORDER BY due_date ASC
            """, (user_id, today))
    overdue_tasks = c.fetchall()
    conn.close()
    return overdue_tasks

def get_events(filter_type = 'all'):
    conn = get_connection()
    c = conn.cursor()
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')

    if filter_type == 'today':
        c.execute("SELECT * FROM events WHERE event_date = ?", (today,))
    elif filter_type == 'upcoming':
        c.execute("SELECT * FROM events WHERE event_date > ?", (today,))
    else:
        c.execute("SELECT * FROM events ORDER BY event_date ASC")

    events = c.fetchall()
    conn.close()
    return events

def get_settings(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return {
            'theme': row[1],
            'font_size': row[2],
            'notifications': bool(row[3]),
        }
    return None

def save_settings(user_id, theme, font_size, notifications):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
              INSERT OR REPLACE INTO settings
              (user_id, theme, font_size, notifications)
              VALUES (?, ?, ?, ?)
        """, (user_id, theme, font_size, int(notifications)))
    conn.commit()
    conn.close()


def setup():
    init_db()
    seed_events()
    