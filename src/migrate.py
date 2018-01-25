from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app, db
from models import AppUser, Token

migrate = Migrate(app, db)
