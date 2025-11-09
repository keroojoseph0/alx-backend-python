from mysql.connector import connect, Error 


class DatabaseConnection:
    def __init__(self, connection):
       self.connect = connection
       
    def __enter__(self):
        return self.connect
    
    def __exit__(self, exc_type, exc_value, traceback):
        return self.connect.close()
    
    
with connect(
    host = 'localhost',
    database = 'users',
    password = 'testpassword',
    port = 3306,
    user = 'root'
) as connection:
    connection_db = DatabaseConnection(connection)