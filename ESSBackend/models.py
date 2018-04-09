from ESSBackend.app import db, Base
from sqlalchemy import Column, Integer, String, \
ForeignKey, Date, DateTime, Float, Text, Boolean

# from sqlalchemy.dialects.postgresq import JSON


class AppUser(Base):
    __tablename__ = 'users'
    email = Column(String(128), primary_key=True)
    password_hash = Column(String(64), nullable=False)
    __table_args__ = {'extend_existing': True}

    def __init__(self, email, password_hash):
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return f'<AppUser: {self.email}>'


class Food(Base):
    __tablename__ = 'foods'
    email = Column(ForeignKey(AppUser.email), primary_key=True)
    name = Column(String(128), primary_key=True)
    mealTime = Column(DateTime, primary_key=True)

    quantity = Column(Float)
    quantityUnits = Column(String(64))
    calories = Column(Integer)
    category = Column(String(64))

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


class JournalEntry(Base):
    __tablename__ = 'journals'
    email = Column(ForeignKey(AppUser.email), primary_key=True)
    title = Column(String(128), primary_key=True)

    created = Column(DateTime, nullable=False)
    edited = Column(DateTime)

    content = Column(Text, nullable=False)

    def __init__(self, email, title, created, content):
        self.email = email
        self.title = title
        self.created = created
        self.content = content

    def __repr__(self):
        return f'<JournalEntry: {self.title} by {self.email} ({self.created})>'


class Commute(Base):
    __tablename__ = 'commutes'
    email = Column(ForeignKey(AppUser.email), primary_key=True)
    arrival = Column(DateTime, primary_key=True)

    method = Column(String(64), nullable=False)
    distance = Column(Float, nullable=False)
    departure = Column(DateTime, nullable=False)

    def __init__(self, email, arrival, departure, method, distance):
        self.email = email
        self.arrival = arrival
        self.departure = departure
        self.method = method
        self.distance = distance

    def __repr__(self):
        return f'<Commute: {self.method} by {self.email} ({self.arrival})'


class WaterCups(Base):
    __tablename__ = 'waters'
    email = Column(ForeignKey(AppUser.email), primary_key=True)
    date = Column(Date, primary_key=True)
    count = Column(Integer, nullable=False)

    def __init__(self, email, date, count=0):
        self.email = email
        self.date = date
        self.count = count

    def __repr__(self):
        return f'<WaterCups: {self.email} drank {self.count} ({self.date})>'


class ShowerUsage(Base):
    __tablename__ = 'showers'
    email = Column(ForeignKey(AppUser.email), primary_key=True)
    date = Column(Date, primary_key=True)
    minutes = Column(Integer, nullable=False)
    cold = Column(Boolean, nullable=False)

    def __init__(self, email, date, minutes, cold=False):
        self.email = email
        self.date = date
        self.minutes = minutes
        self.cold = cold

    def __repr__(self):
        return f'<ShowerUsage: {self.email} for {self.minutes} ({self.date})>'


class EntertainmentUsage(Base):
    __tablename__ = 'entertainments'
    email = Column(ForeignKey(AppUser.email), primary_key=True)
    date = Column(Date, primary_key=True)
    hours = Column(Integer, nullable=False)

    def __init__(self, email, date, hours):
        self.email = email
        self.date = date
        self.hours = hours

    def __repr__(self):
        return f'<EntertainmentUsage: {self.email} for {self.hours} ({self.date})>'


class Health(Base):
    __tablename__ = 'health_logs'
    email = Column(ForeignKey(AppUser.email), primary_key=True)
    date = Column(Date, primary_key=True)
    cigarettes = Column(Integer, default=0)

    def __init__(self, email, date, cigarettes):
        self.email = email
        self.date = date
        self.cigarettes = cigarettes

    def __repr__(self):
        return f'<Health: {self.email} smoked {self.cigarettes} ({self.date})>'


# class JournalAttachment(Base()):
#     path = Column(String(256), primary_key=True)
#     pass

# class FoodAttachment(Base()):
#     path = Column(String(256), primary_key=True)
#     pass
