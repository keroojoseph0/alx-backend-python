import csv
import mysql.connector
from mysql.connector import Error


def connect_db():
    
    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            port = '3306',
            user = 'root',
            password = 'SecureP@sw0rd!123'
        ) 
        
        if connection.is_connected():
            print('connection successful')
        
    except Error as e:
        print(e)


connection = connect_db()

def create_database(connection):
    try:
        cursor = connection.cursor()
        
        cursor.execute (
            "CREATE DATABASE IF NOT EXISTS ALX_prodev"
        )
        
        if connection.is_connected():
            print('Table user_data created successfully')
        
    except Error as e:
        print(e)
    
    finally:
        cursor.close()
        connection.close()
    
def connect_to_prodev():    
    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            port = '3306',
            user = 'root',
            database = 'ALX_prodev',
            password = 'SecureP@sw0rd!123'
        ) 
        
        if connection.is_connected():
            print('Database ALX_prodev is present ')
        
    except Error as e:
        print(e)
        
def create_table(connection):
    try:
        cursor = connection.cursor()
        
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXIST user_data (
                user_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                age DECIMAL(3,0) NOT NULL
            );
            '''
        )
    except Error as e:
        print(e)
        
def insert_data(connection, data):
    try:
        cursor = connection.cursor()
        
        with open(data, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # skip header row if file has one

            for row in reader:
                cursor.execute(
                    "INSERT INTO user_data (name, email, age) VALUES (%s, %s, %d)",
                    row
                )
        
    except Error as e:
        print(e)