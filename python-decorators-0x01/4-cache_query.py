import time
import sqlite3 
import functools


query_cache = {}

"""your code goes here"""

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


def cache_query(func):
    @functools.lru_cache(maxsize=100)
    def wrapper(conn, query, *args, **kwargs):
        func(conn, query, *args, **kwargs)
        
    return wrapper



@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")