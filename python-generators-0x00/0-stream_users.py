import mysql.connector
from mysql.connector import Error


def stream_users():
    """
    Generator function that fetches rows one by one from the user_data table.
    Yields:
        tuple: A single row from the user_data table.
    """
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",           # change if needed
            password="SecureP@sword!123",   # change if needed
            database="ALX_prodev"
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_data;")

            # Use a single loop to yield rows one by one
            for row in cursor:
                yield row

    except Error as e:
        print(f"Database error: {e}")

    finally:
        cursor.close()
        connection.close()