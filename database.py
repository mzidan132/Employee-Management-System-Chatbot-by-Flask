from flask import g
import sqlite3

def connect_to_database():
    sql = sqlite3.connect('C:/Users/mdzid/Downloads/Documents/flask/crud_application_flask/crudapplication.db')
    sql.row_factory = sqlite3.Row
    return sql 

def get_database():
    if not hasattr(g, 'crudapplication_db'):
        g.crudapplication_db = connect_to_database()
    return g.crudapplication_db

def execute_sql(sql_command):
    db = get_database()
    cursor = db.cursor()
    cursor.execute(sql_command)
    db.commit()
    cursor.close()

