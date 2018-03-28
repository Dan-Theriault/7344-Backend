from ESSBackend.app import db

# from sqlalchemy.dialects.postgresq import JSON


class AppUser(db.Model):
    email = db.Column(db.String(128), primary_key=True)
    password_hash = db.Column(db.String(64), nullable=False)
    __table_args__ = {'extend_existing': True}

    def __init__(self, email, password_hash):
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return f'<AppUser: {self.email}>'


class Food(db.Model):
    email = db.Column(db.ForeignKey(AppUser.email), primary_key=True)
    name = db.Column(db.String(128), primary_key=True)
    mealTime = db.Column(db.DateTime, primary_key=True)

    quantity = db.Column(db.Float)
    quantityUnits = db.Column(db.String(64))
    calories = db.Column(db.Integer)
    category = db.Column(db.String(64))

    def __init__(
        self,
        email,
        name,
        mealTime,
        quantity=1.0,
        quantityUnits='UNIT',
        calories=None,
        category=None
    ):
        self.email = email
        self.name = name
        self.mealTime = mealTime
        self.quantity = quantity
        self.quantityUnits = quantityUnits
        self.calories = calories
        self.category = category

    def __repr__(self):
        return f'<Food: {self.name} for {self.email} ({self.mealTime})>'


class JournalEntry(db.Model):
    email = db.Column(db.ForeignKey(AppUser.email), primary_key=True)
    title = db.Column(db.String(128), primary_key=True)

    created = db.Column(db.DateTime, nullable=False)
    edited = db.Column(db.DateTime)

    content = db.Column(db.Text, nullable=False)

    def __init__(self, email, title, created, content):
        self.email = email
        self.title = title
        self.created = created
        self.content = content

    def __repr__(sefl):
        return f'<JournalEntry: {self.title} by {self.email} ({self.created})>'


class Commute(db.Model):
    email = db.Column(db.ForeignKey(AppUser.email), primary_key=True)
    arrival = db.Column(db.DateTime, primary_key=True)

    method = db.Column(db.String(64), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    departure = db.Column(db.DateTime, nullable=False)

    def __init__(self, email, arrival, departure, method, distance):
        self.email = email
        self.arrival = arrival
        self.departure = departure
        self.method = method
        self.distance = distance

    def __repr__(self):
        return f'<Commute: {self.method} by {self.email} ({self.arrival})'


# class JournalAttachment(db.Model()):
#     path = db.Column(db.String(256), primary_key=True)
#     pass

# class FoodAttachment(db.Model()):
#     path = db.Column(db.String(256), primary_key=True)
#     pass
