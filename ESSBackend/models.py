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


class Token(db.Model):
    email = db.Column(
        db.String(120), db.ForeignKey(AppUser.email), nullable=False)

    created = db.Column(db.DateTime, primary_key=True)
    hash = db.Column(db.String(64), nullable=False)  # HMAC?
    __table_args__ = {'extend_existing': True}

    def __init___(self, email, created, hash):
        self.email = email
        self.created = created
        self.hash = hash

    def __repr__(self):
        return f'<Token {self.hash}, {self.email}, {self.created}>'
