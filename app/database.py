import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'factory'),
    'pool_name': 'rule_engine_pool',
    'pool_size': 5,
    'pool_reset_session': True,
    'charset': 'utf8mb4',
    'use_unicode': True,
    'connect_timeout': 30,
}

# Connection pool
connection_pool = None


def get_connection_pool():
    """Get or create the database connection pool."""
    global connection_pool
    if connection_pool is None:
        try:
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
            print("Connection pool created successfully")
        except Error as e:
            print(f"Error creating connection pool: {e}")
            raise
    return connection_pool


def get_connection():
    """Get a connection from the pool."""
    pool = get_connection_pool()
    try:
        connection = pool.get_connection()
        return connection
    except Error as e:
        print(f"Error getting connection from pool: {e}")
        raise


def test_connection():
    """Test the database connection."""
    try:
        conn = get_connection()
        if conn.is_connected():
            print("Database connected successfully!")
            conn.close()
            return True
    except Error as e:
        print(f"Error connecting to database: {e}")
        return False
    return False


def execute_query(query, params=None, fetch=True):
    """Execute a query and return results."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount  # Return row count instead of lastrowid
        return result
    except Error as e:
        conn.rollback()
        print(f"Error executing query: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def execute_query_single(query, params=None):
    """Execute a query and return a single result."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"Error executing query: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
