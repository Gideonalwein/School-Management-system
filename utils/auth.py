import bcrypt
from sqlalchemy import select
from config import ROLES

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(username, password, role):
    session = get_session()
    try:
        if role not in ROLES:
            return False, "Invalid role"
        hashed = hash_password(password)
        session.execute(f"""
            INSERT INTO users (username, password, role) VALUES (?, ?, ?)
        """, (username, hashed, role))
        session.commit()
        return True, "User registered successfully"
    except Exception as e:
        return False, str(e)

def authenticate_user(username, password):
    session = get_session()
    user = session.execute(f"SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user and check_password(password, user['password']):
        return dict(user)
    return None
