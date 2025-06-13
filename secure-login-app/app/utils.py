from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from werkzeug.utils import secure_filename
from . import db
from .models import User
from flask import current_app

ph = PasswordHasher()

def hash_password(password):
    return ph.hash(password)

def verify_password(hash, password):
    try:
        ph.verify(hash, password)
        return True
    except VerifyMismatchError:
        return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_user_photo(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_data = file.read()
        if len(file_data) > current_app.config['MAX_CONTENT_LENGTH']:
            return None  # File too large
        return file_data
    return None