from flask import request
import requests, sqlite3
def handler(cursor):
    host=request.form.get("host")
    return requests.post("http://"+host).text
