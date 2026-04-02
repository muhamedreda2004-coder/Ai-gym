import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


class DatabaseHandler:
    def __init__(self, db_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = db_path or os.getenv('SQLITE_DB_PATH', os.path.join(base_dir, 'database.db'))
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    full_name TEXT,
                    email TEXT,
                    height TEXT,
                    weight TEXT,
                    age TEXT,
                    gender TEXT,
                    fitness_goal TEXT,
                    training_days TEXT,
                    activity_level TEXT,
                    injuries TEXT,
                    allergies TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Database init error: {e}")

    def create_user(self, full_name, username, email, password):
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (full_name, username, email, password) VALUES (?, ?, ?, ?)",
                (full_name, username, email, generate_password_hash(password))
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Create user error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user(self, username):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return dict(row) if row else None

    def verify_user(self, username, password):
        user = self.get_user(username)
        if user and check_password_hash(user['password'], password):
            return user
        return None

    def update_user_data(self, username, data):
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE users
                SET height = ?, weight = ?, age = ?, gender = ?, fitness_goal = ?,
                    training_days = ?, activity_level = ?
                WHERE username = ?
                """,
                (
                    str(data.get('height', '')),
                    str(data.get('weight', '')),
                    str(data.get('age', '')),
                    str(data.get('gender', '')),
                    str(data.get('goal', '')),
                    str(data.get('training_days', '')),
                    str(data.get('activity_level', '')),
                    username,
                ),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Update error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def update_extra_data(self, username, extra_data):
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE users
                SET injuries = ?, allergies = ?
                WHERE username = ?
                """,
                (
                    str(extra_data.get('injuries', '')),
                    str(extra_data.get('allergies', '')),
                    username,
                ),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Update extra data error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
