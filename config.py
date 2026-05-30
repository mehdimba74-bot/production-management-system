import os

class Config:
    SECRET_KEY = 'your-secret-key-change-this-12345'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///production.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False