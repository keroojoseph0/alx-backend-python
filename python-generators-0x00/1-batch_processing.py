import mysql.connector
from mysql.connector import Error


def stream_users_in_batches(batch_size):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",           
            password="SecureP@sw0rd!123",   
            database="ALX_prodev"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute (
                f"SELECT * FROM user_data LIMIT {batch_size}"
            )
        
        for row in cursor:
            yield row
            
    except Error as e:
        return (e)


def batch_processing(batch_size):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",           
            password="SecureP@sw0rd!123",   
            database="ALX_prodev"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute (
                f"SELECT * FROM user_data WHERE age > 25 LIMIT {batch_size}"
            )
        
        for row in cursor:
            yield row
            
    except Error as e:
        return (e)