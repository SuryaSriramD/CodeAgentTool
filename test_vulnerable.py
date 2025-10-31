import os
import pickle

# Hardcoded credentials - SECURITY ISSUE
API_KEY = 'sk-12345abcdef'
DB_PASSWORD = 'admin123'

def run_command(user_input):
    # Command injection vulnerability
    os.system(f'ls {user_input}')

def load_data(filename):
    # Unsafe deserialization
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data
