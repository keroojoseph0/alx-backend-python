from mysql.connector import connect, Error 


class ExecuteQuery:
    def __init__(self, connection, query, paramter):
       self.connect = connection
       cursor = self.connect.cursor()
       result = cursor.execute(query, (paramter))
       return result
       
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
    connection_db = ExecuteQuery(connection, 'SELECT * FROM users WHERE age > %s', 25)
