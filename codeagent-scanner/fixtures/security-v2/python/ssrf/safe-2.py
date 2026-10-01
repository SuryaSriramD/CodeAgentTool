from flask import request
import requests, sqlite3
def handler(cursor):
    return requests.post("https://service.example/events",json={"x":1}).text
