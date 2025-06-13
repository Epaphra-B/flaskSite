from . import db
from sqlalchemy.sql import func
import random
import string

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(6), unique=True, nullable=False)  # 6-digit username
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_photo = db.Column(db.LargeBinary, nullable=True)  # Path to photo
    created_at = db.Column(db.DateTime, server_default=func.now())

    def __init__(self, first_name, middle_name, last_name, email, password_hash, user_photo=None):
        self.first_name = first_name.upper()
        self.middle_name = middle_name.upper() if middle_name else None
        self.last_name = last_name.upper()
        self.email = email.lower()
        self.password_hash = password_hash
        self.user_photo = user_photo
        self.user_id = self.generate_user_id()

    @staticmethod
    def generate_user_id():
        while True:
            user_id = ''.join(random.choices(string.digits, k=6))
            if not User.query.filter_by(user_id=user_id).first():
                return user_id