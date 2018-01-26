# boilerplate from https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    SECRET_KEY = "Not actually a secret ;_;"
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    TOKEN_TIMEOUT = "???"  # set this to a timedelta
    # significant performance impact & not needed
    SQLALCHEMY_TRACK_MODIFICATIONS = False
