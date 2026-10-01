from flask import request
import requests, sqlite3
def handler(cursor):
    url=request.args.get("url")
    return requests.get(url).text
