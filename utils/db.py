import sqlite3
from config import DB_NAME
import os
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'school.db')

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)
