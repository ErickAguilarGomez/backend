import mysql.connector

def get_db_connection():
    conexion = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='clientes'
    )
    return conexion