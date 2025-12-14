import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="minjunwon9014@",
        database="pet_ai",
        cursorclass=pymysql.cursors.DictCursor
    )