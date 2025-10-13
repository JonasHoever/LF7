import mysql.connector as mysql
from src.db_config import get_connection

class Init():
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key NOT NULL, nfc_tag VARCHAR(255) unique NOT NULL, pin VARCHAR(255) DEFAULT NULL, name varchar(255), surname varchar(255), active tinyint default 1, creation_stamp datetime DEFAULT CURRENT_TIMESTAMP);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS user_data(session_id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, checkin_time DATETIME, checkout_time DATETIME, date DATE DEFAULT CURRENT_DATE, status tinyint DEFAULT 1, session_duration FLOAT, FOREIGN KEY (user_id) REFERENCES users(id))")
    def del_tables(self):
        self.cursor.execute("DROP TABLE IF EXISTS user_data")
        self.cursor.execute("DROP TABLE IF EXISTS users;")
    def init_db(self):
        self.del_tables()
        self.create_tables()
        self.conn.close()