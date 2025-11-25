import pymysql  # 使用 MariaDB 連接庫
def connect_to_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        db="Mouse",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def create_db():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="123456"
    )
    cur = conn.cursor()

    cur.execute("CREATE DATABASE IF NOT EXISTS Mouse")
    conn.commit()
    conn.close()

def drop_and_create_table():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Coordinates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            x INT NOT NULL,
            y INT NOT NULL,
            delta_x INT NOT NULL,
            delta_y INT NOT NULL,
            direction VARCHAR(10) NOT NULL
            
        )
    """)
    conn.commit()
    conn.close()  # 確保關閉連接


    
