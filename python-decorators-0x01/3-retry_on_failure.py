import time
import sqlite3 
import functools

#### paste your with_db_decorator here

""" your code goes here"""
def with_db_connection(func):
    
    @functools.wraps(func)
    def wrapper(conn, user_id, new_email, *args, **kwargs):
        try:
            with sqlite3.connect('users.db') as conn:
                func(conn, user_id, new_email, *args, **kwargs)
        
        except sqlite3.Error as e:
            print(e)
            
        finally:
            conn.close()

    return wrapper


def retry_on_failure(func, retries=3, delay=1):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            
            for i in range(retries):
                func(conn, *args, **kwargs)
                i += 1
                time.sleep(delay)
                
        except Exception as e:
            raise(e)
            
        
        
@with_db_connection
@retry_on_failure(retries=3, delay=1)

def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)