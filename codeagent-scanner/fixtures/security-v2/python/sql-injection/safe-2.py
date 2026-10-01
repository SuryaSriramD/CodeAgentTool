from flask import request
import requests, sqlite3
def handler(cursor):
    cursor.execute("SELECT count(*) FROM users")
