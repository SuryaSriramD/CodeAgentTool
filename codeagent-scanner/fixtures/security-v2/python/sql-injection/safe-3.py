from flask import request
import requests, sqlite3
def handler(cursor):
    name = request.form.get("name")
    print(name)
