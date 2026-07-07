import mysql.connector
from mysql.connector import Error
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Kasturi123#"),
    "database": os.getenv("DB_NAME", "stock_project"),
}

def get_db_connection():
    """Get a MySQL database connection."""
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn

def init_db():
    """Initialize database and create tables if they don't exist."""
    try:
        # First connect without database to create it if needed
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.close()
        conn.close()

        # Now connect with database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                price DECIMAL(10, 2),
                sentiment_label VARCHAR(20),
                sentiment_score DECIMAL(5, 2),
                volatility DECIMAL(5, 2),
                risk_level VARCHAR(20),
                recommendation VARCHAR(20),
                explanation TEXT,
                predicted_price DECIMAL(10, 2),
                evs_score DECIMAL(5, 1),
                evs_level VARCHAR(20),
                investor_type VARCHAR(20),
                ml_accuracy DECIMAL(5, 1),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Database init error: {e}")
        return False

def save_report(symbol, price, sentiment_label, sentiment_score, volatility,
                risk_level, recommendation, explanation, predicted_price=0,
                evs_score=0, evs_level="N/A", investor_type="moderate", ml_accuracy=0):
    """Save analysis report to database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO stock_reports (symbol, price, sentiment_label, sentiment_score,
                volatility, risk_level, recommendation, explanation, predicted_price,
                evs_score, evs_level, investor_type, ml_accuracy)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (symbol, price, sentiment_label, sentiment_score, volatility,
              risk_level, recommendation, explanation, predicted_price,
              evs_score, evs_level, investor_type, ml_accuracy))
        conn.commit()
        inserted_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return inserted_id
    except Error as e:
        print(f"DB save error: {e}")
        return None

def get_recent_reports(limit: int = 10) -> list:
    """Fetch recent reports from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM stock_reports ORDER BY created_at DESC LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Convert datetime to string
        for row in rows:
            if row.get("created_at"):
                row["created_at"] = str(row["created_at"])
        return rows
    except Error as e:
        print(f"DB fetch error: {e}")
        return []
