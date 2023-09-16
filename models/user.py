from db import db

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True) # id is a column in the users table.
    username = db.Column(db.String(80), unique=True, nullable=False) # username is a column in the users table.
    password = db.Column(db.String(80), unique=False, nullable=False) # password is a column in the users table.