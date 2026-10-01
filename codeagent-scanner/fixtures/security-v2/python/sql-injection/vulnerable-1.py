from flask import request
import requests, sqlite3
def handler(cursor):
    name = request.args.get("name")
    cursor.execute("SELECT * FROM users WHERE name = '" + name + "'")
