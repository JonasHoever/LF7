import mysql.connector as mysql
from src.db_config import get_connection

class Init():
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        self.cursor.execute("CREATE TABLE users (id int auto_increment primary key NOT NULL, nfc_tag bigint unique NOT NULL, pin varchar(255), active tinyint default 1);")
        self.cursor.execute("CREATE TABLE user_data(session_id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, checkin_time DATETIME, checkout_time DATETIME, date DATE DEFAULT CURRENT_DATE, status tinyint DEFAULT 1, FOREIGN KEY (user_id) REFERENCES users(id))")
    def del_tables(self):
        self.cursor.execute("DROP TABLE IF EXISTS user_data")
        self.cursor.execute("DROP TABLE IF EXISTS users;")
    def init_db(self):
        self.del_tables()
        self.create_tables()
        self.conn.close()