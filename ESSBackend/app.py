# RESTful API for our application
# Guided by several online resources:
# - https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

# Comments Post-Review RE: Code Review
#
# Several of the reported issues are #WONTFIX.
# In particular, some typographic concerns did not respect PEP8,
# the official python style guide.
# This project is auto-formatted with YAPF to follow PEP8
# (with maximum line length increased to 100 chars)
#
# 1. "breaking convention of spacing for jsonify":
#    This project's convention is to split lines past 100 characters.
# 2. "Sometimes CamelCase, sometimes underscore_separate"
#    PEP8 indicates that classes should follow CamelCase.
#    Functions and variables should follow underscore_separate.
# 3. "no spaces before or after ="
#    This is done inside function calls,
#    and differentiaties from normal variable assignment.
#
# One functional concern was also unfounded:
# 1. "ignore db response when returning result"
#    Result does not consider whether any content was found,
#    only whether the operation was successful.
#    Finding no content is still a successful operation; no error occurs.

from ESSBackend.config import Config
from bcrypt import checkpw, hashpw, gensalt
from datetime import datetime
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, cast, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from typing import NamedTuple, List, Dict

import hashlib

app = Flask(__name__)
app.config.from_object(Config)

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, convert_unicode=True)
db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db.query_property()


def db_init():
    import ESSBackend.models
    Base.metadata.create_all(bind=engine)


# Called after all API responses
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()


@app.route('/api/login', methods=['POST'])
def login():
    from ESSBackend.models import AppUser

    requirements = [('email', []), ('password', [])]
    check = check_requirements(requirements, request)
    if not check[0]:
        return check[1]

    user: AppUser = AppUser.query.filter_by(email=request.json['email']).first()
    if not user:
        return make_response(jsonify({'result': False, 'message': 'User not found'}))

    if checkpw(request.json['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return return_token(user.email)
    else:
        return make_response(jsonify({'result': False, 'message': 'Incorrect Password'}))


@app.route('/api/register', methods=['POST'])
def register():
    from ESSBackend.models import AppUser
    requirements = [('email', []), ('password', [])]
    check = check_requirements(requirements, request)
    if not check[0]:
        return check[1]

    user: AppUser = AppUser.query.filter_by(email=request.json['email']).first()
    if user:
        return make_response(jsonify({'result': False, 'message': 'User already exists'}))

    pwhash = (hashpw(request.json['password'].encode('utf-8'), gensalt())).decode('utf-8')
    new_user: AppUser = AppUser(password_hash=pwhash, email=request.json['email'])
    db.add(new_user)
    db.commit()

    return return_token(new_user.email)


@app.route('/api/status', methods=['GET'])
def status():
    return make_response(jsonify({'result': True, 'message': 'Server status normal'}))


# ----- Food Functions


@app.route('/api/food', methods=['POST'])
def get_food():
    requirements = [
        ('date', []),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import Food

    foods = Food.query.filter(
        cast(Food.mealTime, Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
        Food.email == request.json['token']['email']
    ).all()

    contentList = [
        {
            'name': food.name,
            'quantity': food.quantity,
            'quantityUnits': food.quantityUnits,
            'calories': food.calories,
            'category': food.category,
            'mealTime': food.mealTime.isoformat()
        } for food in foods
    ]

    return make_response(
        jsonify(
            {
                'result': True,
                'message': f"Returning all commutes found for {request.json['date']}",
                'list': contentList
            }
        )
    )


@app.route('/api/food/new', methods=['POST'])
def post_food():
    requirements = [
        ('content', ['name', 'quantity', 'quantityUnits', 'calories', 'category', 'mealTime']),
        ('metadata', ['timestamp']),
        ('token', ['hash', 'expiry', 'email']),
    ]
    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import Food
    food: Food = Food.query.filter_by(
        email=request.json['token']['email'],
        name=request.json['content']['name'],
        mealTime=request.json['content']['mealTime']
    ).first()

    if food:
        food.quantity = request.json['content']['quantity']
        food.quantityUnits = request.json['content']['quantityUnits']
        food.calories = request.json['content']['calories']
        food.category = request.json['content']['category']
        db.commit()
        return make_response(jsonify({'result': True, 'message': 'Updated existing food.'}))
    else:
        new_food: Food = Food(
            email=request.json['token']['email'],
            name=request.json['content']['name'],
            mealTime=request.json['content']['mealTime'],
            quantity=request.json['content']['quantity'],
            quantityUnits=request.json['content']['quantityUnits'],
            calories=request.json['content']['calories'],
            category=request.json['content']['category']
        )
        db.add(new_food)
        db.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new food.'}))


# ----- Commute Functions


@app.route('/api/commute', methods=['POST'])
def get_commute():
    requirements = [
        ('date', []),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import Commute

    commutes = Commute.query.filter(
        cast(Commute.arrival, Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
        Commute.email == request.json['token']['email']
    ).all()

    contentList = [
        {
            'method': commute.method,
            'distance': commute.distance,
            'departure': commute.departure,
            'arrival': commute.arrival,
        } for commute in commutes
    ]

    return make_response(
        jsonify(
            {
                'result': True,
                'message': f"Returning all commutes found for {request.json['date']}",
                'list': contentList
            }
        )
    )


@app.route('/api/commute/new', methods=['POST'])
def post_commute():
    requirements = [
        ('content', ['arrival', 'departure', 'method', 'distance']),
        ('metadata', ['timestamp']),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import Commute

    commute: Commute = Commute.query.filter_by(
        email=request.json['token']['email'],
        arrival=request.json['content']['arrival'],
    ).first()

    if commute:
        commute.arrival = request.json['content']['arrival']
        commute.departure = request.json['content']['departure']
        commute.method = request.json['content']['method']
        commute.distance = request.json['content']['distance']
        db.commit()
        return make_response(jsonify({'result': True, 'message': 'Updated existing commute.'}))
    else:
        new_commute: Commute = Commute(
            email=request.json['token']['email'],
            arrival=request.json['content']['arrival'],
            departure=request.json['content']['departure'],
            method=request.json['content']['method'],
            distance=request.json['content']['distance']
        )
        db.add(new_commute)
        db.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new commute.'}))


# ----- Journal Functions


@app.route('/api/journal', methods=['POST'])
def get_journal():
    requirements = [
        ('date', []),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import JournalEntry

    journals = JournalEntry.query.filter(
        cast(JournalEntry.created, Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
        JournalEntry.email == request.json['token']['email']
    ).all()

    contentList = [
        {
            'contents': journal.content,
            'title': journal.title,
            'created': journal.created,
            'edited': journal.edited
        } for journal in journals
    ]

    return make_response(
        jsonify(
            {
                'result': True,
                'message': f"Returning all journals found for {request.json['date']}",
                'list': contentList
            }
        )
    )


@app.route('/api/journal/new', methods=['POST'])
def post_journal():
    requirements = [
        ('content', ['title', 'contents']),
        ('metadata', ['timestamp']),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import JournalEntry

    journal: JournalEntry = JournalEntry.query.filter_by(
        email=request.json['token']['email'],
        title=request.json['content']['title'],
    ).first()

    if journal:
        journal.content = request.json['content']['contents']
        journal.edited = request.json['metadata']['timestamp']
        db.commit()
        return make_response(
            jsonify({
                'result': True,
                'message': 'Updated existing journal entry.'
            })
        )
    else:
        new_journal: JournalEntry = JournalEntry(
            email=request.json['token']['email'],
            created=request.json['metadata']['timestamp'],
            title=request.json['content']['title'],
            content=request.json['content']['contents']
        )
        db.add(new_journal)
        db.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new journal entry.'}))


# ----- Water Functions
@app.route('/api/water', methods=['POST'])
def get_water():
    requirements = [
        ('date', []),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import WaterCups

    water = WaterCups.query.filter(
        cast(WaterCups.date, Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
        WaterCups.email == request.json['token']['email']
    ).first()

    if water:
        waterContent = {'cupsCount': water.count, 'isIncrement': False}
    else:
        waterContent = {'cupsCount': 0, 'isIncrement': False}

    return make_response(
        jsonify(
            {
                'result': True,
                'message': f"Returning water consumption for {request.json['date']}",
                'content': waterContent
            }
        )
    )


@app.route('/api/water/new', methods=['POST'])
def post_water():
    requirements = [
        ('content', ['isIncrement', 'cups']),
        ('metadata', ['timestamp']),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import WaterCups

    water: WaterCups = WaterCups.query.filter_by(
        email=request.json['token']['email'],
        date=request.json['metadata']['timestamp'],  # TODO: timestamp equality
    ).first()

    if water:
        if request.json['content']['isIncrement']:
            water.count += request.json['content']['cups']
        else:
            water.count = request.json['content']['cups']
        db.commit()
        return make_response(jsonify({'result': True, 'message': 'Updated existing water entry.'}))
    else:
        new_water: WaterCups = WaterCups(
            email=request.json['token']['email'],
            date=request.json['metadata']['timestamp'],
            count=request.json['content']['cups']
        )
        db.add(new_water)
        db.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new water entry.'}))


# ----- Shower Functions
@app.route('/api/showers', methods=['POST'])
def get_shower():
    requirements = [
        ('date', []),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import ShowerUsage

    shower = ShowerUsage.query.filter(
        cast(ShowerUsage.date, Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
        ShowerUsage.email == request.json['token']['email']
    ).first()

    if shower:
        showerContent = {'minutes': shower.minutes, 'cold': shower.cold}
    else:
        showerContent = {'minutes': 0, 'cold': False}

    return make_response(
        jsonify(
            {
                'result': True,
                'message': f"Returning shower usage for {request.json['date']}",
                'content': showerContent
            }
        )
    )


@app.route('/api/showers/new', methods=['POST'])
def post_shower():
    requirements = [
        ('content', ['cold', 'minutes']),
        ('metadata', ['timestamp']),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import ShowerUsage

    shower: ShowerUsage = ShowerUsage.query.filter_by(
        email=request.json['token']['email'],
        date=request.json['metadata']['timestamp'],  # TODO: timestamp equality
    ).first()

    if shower:
        shower.minutes = request.json['content']['minutes']
        shower.cold = request.json['content']['cold']
        db.commit()
        return make_response(jsonify({'result': True, 'message': 'Updated existing shower entry.'}))
    else:
        new_shower: ShowerUsage = ShowerUsage(
            email=request.json['token']['email'],
            date=request.json['metadata']['timestamp'],
            minutes=request.json['content']['minutes'],
            cold=request.json['content']['cold']
        )
        db.add(new_shower)
        db.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new shower entry.'}))


# ----- Entertainment Functions
@app.route('/api/entertainment', methods=['POST'])
def get_entertainment():
    requirements = [
        ('date', []),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import EntertainmentUsage

    entertainment = EntertainmentUsage.query.filter(
        cast(EntertainmentUsage.date, Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
        EntertainmentUsage.email == request.json['token']['email']
    ).first()

    if entertainment:
        entertainmentContent = {'hours': entertainment.hours}
    else:
        entertainmentContent = {'hours': 0}

    return make_response(
        jsonify(
            {
                'result': True,
                'message': f"Returning entertainment usage for {request.json['date']}",
                'content': entertainmentContent
            }
        )
    )


@app.route('/api/entertainment/new', methods=['POST'])
def post_Entertainment():
    requirements = [
        ('content', ['hours']),
        ('metadata', ['timestamp']),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import EntertainmentUsage

    entertainment: EntertainmentUsage = EntertainmentUsage.query.filter_by(
        email=request.json['token']['email'],
        date=request.json['metadata']['timestamp'],  # TODO: timestamp equality
    ).first()

    if entertainment:
        entertainment.hours = request.json['content']['hours']
        db.commit()
        return make_response(
            jsonify({
                'result': True,
                'message': 'Updated existing entertainment entry.'
            })
        )
    else:
        new_entertainment: EntertainmentUsage = EntertainmentUsage(
            email=request.json['token']['email'],
            date=request.json['metadata']['timestamp'],
            hours=request.json['content']['hours'],
        )
        db.add(new_entertainment)
        db.commit()
        return make_response(
            jsonify({
                'result': True,
                'message': 'Inserted new entertainment entry.'
            })
        )


# ----- Health Functions
@app.route('/api/health', methods=['POST'])
def get_health():
    requirements = [
        ('date', []),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import Health

    health = Health.query.filter(
        cast(Health.date, Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
        Health.email == request.json['token']['email']
    ).first()

    if health:
        healthContent = {'cigarettes': health.cigarettes}
    else:
        healthContent = {'cigarettes': 0}

    return make_response(
        jsonify(
            {
                'result': True,
                'message': f"Returning health  for {request.json['date']}",
                'content': healthContent
            }
        )
    )


@app.route('/api/health/new', methods=['POST'])
def post_health():
    requirements = [
        ('content', ['cigarettes']),
        ('metadata', ['timestamp']),
        ('token', ['hash', 'expiry', 'email']),
    ]

    req_check = check_requirements(requirements, request)
    if not req_check[0]:
        return req_check[1]

    token: Token = request.json['token']
    tok_check = check_token(token)
    if not tok_check[0]:
        return tok_check[1]

    from ESSBackend.models import Health

    health: Health = Health.query.filter_by(
        email=request.json['token']['email'],
        date=request.json['metadata']['timestamp'],  # TODO: timestamp equality
    ).first()

    if health:
        health.cigarettes = request.json['content']['cigarettes']
        db.commit()
        return make_response(jsonify({'result': True, 'message': 'Updated existing health entry.'}))
    else:
        new_health: Health = Health(
            email=request.json['token']['email'],
            date=request.json['metadata']['timestamp'],
            cigarettes=request.json['content']['cigarettes'],
        )
        db.add(new_health)
        db.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new health entry.'}))


# ----- Utility Functions


def check_token(token: Dict[str, str]):
    # TODO: Token expiry
    new_hash = hashlib.sha256(
        (token['expiry'] + token['email'] + app.config['SECRET_KEY']).encode('utf-8')
    ).hexdigest()

    return (
        token['hash'] == new_hash,
        make_response(jsonify({
            'result': False,
            'message': f'Invalid Token Hash: {new_hash}'
        }))
    )


def check_requirements(requirements: List[str], request):
    if not request.json:
        return (False, make_response(jsonify({'result': False, 'message': 'Where\'s the JSON?'})))

    for req in requirements:
        if req[0] not in request.json:
            return (
                False,
                make_response(
                    jsonify({
                        'result': False,
                        'message': f'Missing required field: {req}'
                    })
                )
            )
        for subreq in req[1]:
            if subreq not in request.json[req[0]]:
                return (False, make_response(jsonify({
                            'result': False,
                            'message': f'Missing required field: {req}.{subreq}'
                        })))  # yapf:disable

    return (True, None)


def return_token(email: str):
    now = (datetime.utcnow()).isoformat()[:-7]
    hmac = hashlib.sha256((str(now) + email + app.config['SECRET_KEY']).encode('utf-8'))

    return make_response(
        jsonify(
            {
                'token': {
                    'hash': hmac.hexdigest(),
                    'email': email,
                    'expiry': now  # TODO: send actual expiry
                },
                'result': True,
                'message': 'Successful Login'
            }
        )
    )


# ----- Error Handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'result': False, 'message': 'Not found'}), 404)


def main():
    app.run(debug=app.config['DEBUG'])


if __name__ == '__main__':
    main()
