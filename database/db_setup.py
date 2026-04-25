import sqlite3

conn = sqlite3.connect("mindscope.db")

cursor = conn.cursor()

# Create users table

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
username TEXT UNIQUE,
email TEXT,
password TEXT
)
""")

# Create emotion logs table

cursor.execute("""
CREATE TABLE IF NOT EXISTS emotion_logs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
user_text TEXT,
face_emotion TEXT,
mental_state TEXT,
insight TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()

print("Database and tables created successfully")