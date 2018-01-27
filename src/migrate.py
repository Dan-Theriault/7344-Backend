from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from ESSBackend.app import app, db
from ESSBackend.models import AppUser, Token

migrate = Migrate(app, db)
