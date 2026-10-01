from flask import request
import requests, sqlite3
def handler(cursor):
    name=request.json["name"]
    return {"name":name}
