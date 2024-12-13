from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
import os

db = SQLAlchemy()
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tailoring-management.db'
    app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    Bootstrap(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app