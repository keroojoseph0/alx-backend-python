from itertools import count
import mysql.connector
from mysql.connector import Error 

def stream_user_ages():
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
                f"SELECT age FROM user_data"
            )
            
            total = 0
            count = 0
            
            for row in cursor:
                total += row[0]
                count += 1
            
            average = total / count if count > 0 else 0
            print('Average age of users:', average)
            
    except Error as e:
        return (e)
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
            
print(stream_user_ages())
