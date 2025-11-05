import sqlite3 
import functools

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


def transactional(func):
    
    @functools.wraps(func)
    def wrapper(conn, user_id, new_email, *args, **kwargs):
        try:
            result = func(conn, user_id, new_email, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
        finally:
            conn.close()
        
    return wrapper


@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
#### Update user's email with automatic transaction handling 

update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')