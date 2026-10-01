from flask import request
import requests, sqlite3
def handler(cursor):
    key = request.form.get("id")
    sql = f"SELECT * FROM users WHERE id={key}"
    cursor.execute(sql)
