from ESSBackend.app import db

# from sqlalchemy.dialects.postgresq import JSON


class AppUser(db.Model):
    email = db.Column(db.String(120), primary_key=True)
    password_hash = db.Column(db.String(64), nullable=False)
    __table_args__ = {'extend_existing': True}

    def __init__(self, email, password_hash):
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return '<AppUser %r>' % self.email
