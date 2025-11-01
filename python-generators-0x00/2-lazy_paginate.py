import mysql.connector
from mysql.connector import Error

def paginate_users(page_size, offset = 0):
    start = (offset - 1) * page_size
    return start
     

def lazy_paginate(page_size):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",           
            password="SecureP@sw0rd!123",   
            database="ALX_prodev"
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary = True)
            offset = 0
            
            while True:
                cursor.execute (
                    f"SELECT * FROM user_data LIMIT {page_size} OFFSET {paginate_users(page_size, offset)}"
                )
                rows = cursor.fatchall()
        
                if not rows:
                    break
                yield rows
                offset += 1
            
    except Error as e:
        return (e)
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()