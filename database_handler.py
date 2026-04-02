import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

class DatabaseHandler:
    def __init__(self, host=None, user=None, password=None, database=None):
        host = host or os.getenv('MYSQL_HOST', 'localhost')
        user = user or os.getenv('MYSQL_USER', 'root')
        password = password or os.getenv('MYSQL_PASSWORD', '000002')
        database = database or os.getenv('MYSQL_DATABASE', 'gymai')

        self.database = database
        self.server_config = {'host': host, 'user': user, 'password': password}
        self.config = {**self.server_config, 'database': self.database}
        self._init_db()

    def _add_column_if_not_exists(self, cursor, table, column, col_def):
        try:
            cursor.execute(f"SHOW COLUMNS FROM {table} LIKE '{column}'")
            if not cursor.fetchone():
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
        except Exception as e:
            print(f"Error adding column {column}: {e}")

    def _init_db(self):
        try:
            # Ensure the MySQL database exists before using it.
            conn = mysql.connector.connect(**self.server_config)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            conn.commit()
            cursor.close()
            conn.close()

            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    email VARCHAR(100),
                    height VARCHAR(10),
                    weight VARCHAR(10),
                    age VARCHAR(5),
                    gender VARCHAR(10),
                    fitness_goal VARCHAR(100),
                    training_days VARCHAR(50),
                    activity_level VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Database init error: {e}")

    def create_user(self, full_name, username, email, password):
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (full_name, username, email, password) VALUES (%s,%s,%s,%s)",
                (full_name, username, email, generate_password_hash(password))
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Create user error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user(self, username):
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user

    def verify_user(self, username, password):
        user = self.get_user(username)
        if user and check_password_hash(user['password'], password):
            return user
        return None

    def update_user_data(self, username, data):
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE users SET 
                height=%s, weight=%s, age=%s, gender=%s, fitness_goal=%s,
                training_days=%s, activity_level=%s
                WHERE username=%s
            """, (
                data.get('height', ''), data.get('weight', ''),
                data.get('age', ''), data.get('gender', ''),
                data.get('goal', ''), data.get('training_days', ''),
                data.get('activity_level', ''), username
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Update error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def update_extra_data(self, username, extra_data):
        conn = mysql.connector.connect(**self.config)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE users SET 
                injuries=%s, allergies=%s
                WHERE username=%s
            """, (
                extra_data.get('injuries', ''),
                extra_data.get('allergies', ''),
                username
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Update extra data error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
