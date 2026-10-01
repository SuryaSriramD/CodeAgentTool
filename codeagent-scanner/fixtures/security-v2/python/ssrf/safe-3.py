from flask import request
import requests, sqlite3
def handler(cursor):
    url=request.json["endpoint"]
    return {"url":url}
