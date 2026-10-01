from flask import request
import requests, sqlite3
def handler(cursor):
    name=request.args.get("name")
    return open("/srv/public/index.txt").read()
