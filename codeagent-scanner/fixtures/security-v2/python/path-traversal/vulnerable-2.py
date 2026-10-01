from flask import request
import requests, sqlite3
def handler(cursor):
    name = request.form.get("file")
    path = "/srv/files/" + name
    return open(path).read()
