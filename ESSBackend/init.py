import ESSBackend.models
from ESSBackend.app import db

db.create_all()
db.session.commit()
