import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="pro1",
        password="AFFE",
        database="pro1"
    )