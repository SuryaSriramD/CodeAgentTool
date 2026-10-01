from flask import request
import requests, sqlite3
def handler(cursor):
    return open("config.txt").read()
