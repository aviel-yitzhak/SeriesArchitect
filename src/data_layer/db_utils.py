import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """
    Establishes a connection to the PostgreSQL database using environment variables.
    Requires DB_HOST, DB_NAME, DB_USER, and DB_PASS to be set in the .env file.
    """
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=5432
    )


def execute_query(query, params=None, fetch=False):
    """
    Executes a modification query (INSERT, UPDATE, DELETE).

    :param query: The SQL query string.
    :param params: Tuple of parameters to prevent SQL injection.
    :param fetch: Boolean, whether to fetch results. Defaults to False.
                  Set to True only if using a RETURNING clause.
    :return: A list of RealDictRow (dictionaries) if fetch=True, otherwise None.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            result = cur.fetchall() if fetch else None
            conn.commit()
            return result
    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()


def fetch_query(query, params=None):
    """
    Executes a read-only query (SELECT) and returns all results.

    :param query: The SQL query string.
    :param params: Tuple of parameters.
    :return: A list of Tuples (access data by index, e.g., row[0]).
             Note: This function uses a standard cursor, NOT a dictionary cursor.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        results = cur.fetchall()
        cur.close()
        return results
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []
    finally:
        if conn:
            conn.close()


def test_connection():
    """
    Simple test function to verify database connectivity.
    Prints a success message if connection is established.
    """
    try:
        conn = get_connection()
        print("Successfully connected to the Series Architect data_layer!")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    test_connection()
