import sqlite3

DB_NAME = "mindscope.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


# -----------------------------
# USER REGISTRATION
# -----------------------------
def register_user(name, username, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO users (name, username, email, password)
        VALUES (?, ?, ?, ?)
        """, (name, username, email, password))

        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        conn.close()
        return False


# -----------------------------
# USER LOGIN
# -----------------------------
def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name FROM users
    WHERE username=? AND password=?
    """, (username, password))

    user = cursor.fetchone()

    conn.close()
    return user


# -----------------------------
# SAVE PREDICTION
# -----------------------------
def save_prediction(user_id, text, face_emotion, mental_state, insight):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO emotion_logs (user_id, user_text, face_emotion, mental_state, insight)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, text, face_emotion, mental_state, insight))

    conn.commit()
    conn.close()


# -----------------------------
# USER HISTORY
# -----------------------------
def get_user_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_text, face_emotion, mental_state, insight, created_at
    FROM emotion_logs
    WHERE user_id=?
    ORDER BY created_at DESC
    """, (user_id,))

    data = cursor.fetchall()

    conn.close()
    return data


# -----------------------------
# ANALYTICS DATA
# -----------------------------
def get_emotion_counts(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT mental_state, COUNT(*)
    FROM emotion_logs
    WHERE user_id=?
    GROUP BY mental_state
    """, (user_id,))

    data = cursor.fetchall()
def get_user_stats(user_id):
    conn = sqlite3.connect("mindscope.db")
    cursor = conn.cursor()

    # Total analyses
    cursor.execute("""
        SELECT COUNT(*) FROM emotion_logs
        WHERE user_id = ?
    """, (user_id,))
    total = cursor.fetchone()[0]

    # Positive count
    cursor.execute("""
        SELECT COUNT(*) FROM emotion_logs
        WHERE user_id = ? AND mental_state = 'Positive'
    """, (user_id,))
    positive = cursor.fetchone()[0]

    # Stress count
    cursor.execute("""
        SELECT COUNT(*) FROM emotion_logs
        WHERE user_id = ? AND mental_state = 'Stress'
    """, (user_id,))
    stress = cursor.fetchone()[0]

    # Last emotion
    cursor.execute("""
        SELECT mental_state FROM emotion_logs
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    last = cursor.fetchone()
    last_emotion = last[0] if last else "N/A"

    conn.close()

    return {
        "total": total,
        "positive": positive,
        "stress": stress,
        "last_emotion": last_emotion
    }
def get_recent_analyses(user_id, limit=5):
    conn = sqlite3.connect("mindscope.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_text, face_emotion, mental_state, created_at
        FROM emotion_logs
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "text": row[0],
            "face_emotion": row[1],
            "mental_state": row[2],
            "created_at": row[3]
        })

    return results
def get_all_analyses(user_id):
    import sqlite3

    conn = sqlite3.connect("mindscope.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_text, face_emotion, mental_state, insight, created_at
        FROM emotion_logs
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "text": row[0],
            "face_emotion": row[1],
            "mental_state": row[2],
            "insight": row[3],
            "created_at": row[4]
        })

    return results