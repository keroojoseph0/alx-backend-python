from mysql.connector import connect, Error 


class ExecuteQuery:
    def __init__(self, connection, query, paramter):
       self.connect = connection
       cursor = self.connect.cursor()
       cursor.execute(query, (paramter))
       
    def __enter__(self):
        return self.connect
    
    def __exit__(self, exc_type, exc_value, traceback):
        return self.connect.close()
    