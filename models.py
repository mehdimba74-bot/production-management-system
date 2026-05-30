from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# مدل کاربر
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(50), nullable=False)  # فروش، برنامه35696418راریزی، طراحی
    full_name = db.Column(db.String(120))
    
    def __repr__(self):
        return f'<User {self.username}>'

# مدل محصول/پروژه
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_type = db.Column(db.String(100), nullable=False)  # نوع محصول
    product_name = db.Column(db.String(100), nullable=False)  # نام محصول
    brand_name = db.Column(db.String(100), nullable=False)  # نام برند
    color = db.Column(db.String(50))  # رنگ
    finish = db.Column(db.String(50))  # مات یا براق
    quantity = db.Column(db.Integer, nullable=False)  # مقدار
    delivery_date = db.Column(db.Date, nullable=False)  # تاریخ تحویل
    status = db.Column(db.String(50), default='درحالnotes/STATUS FINAL PUpperwrapped status/ In Process? INTERACTIVE_STATUS! <~ محا