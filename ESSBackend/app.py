# RESTful API for our application
# Guided by several online resources:
# - https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

from bcrypt import checkpw, hashpw, gensalt
from ESSBackend.config import Config
from datetime import datetime
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from typing import NamedTuple, List, Dict

import hashlib

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)


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
    newUser: AppUser = AppUser(password_hash=pwhash, email=request.json['email'])
    db.session.add(newUser)
    db.session.commit()

    return return_token(newUser.email)


@app.route('/api/status', methods=['GET'])
def status():
    return make_response(jsonify({'result': True, 'message': 'Server status normal'}))


# ----- Food Functions


@app.route('/api/food', methods=['POST'])
def getFood():
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
        db.cast(Food.mealTime, db.Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
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
def postFood():
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
        db.session.commit()
        return make_response(jsonify({'result': True, 'message': 'Updated existing food.'}))
    else:
        newFood: Food = Food(
            email=request.json['token']['email'],
            name=request.json['content']['name'],
            mealTime=request.json['content']['mealTime'],
            quantity=request.json['content']['quantity'],
            quantityUnits=request.json['content']['quantityUnits'],
            calories=request.json['content']['calories'],
            category=request.json['content']['category']
        )
        db.session.add(newFood)
        db.session.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new food.'}))


# ----- Commute Functions


@app.route('/api/commute', methods=['POST'])
def getCommute():
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
        db.cast(Commute.arrival, db.Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
        Commute.email == request.json['token']['email']
    ).all()

    contentList = [
        {
            'method': commute.method,
            'distance': commute.distance,
            'departure': commute.departure.isoformat(),
            'arrival': commute.arrival.isoformat(),
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
def postCommute():
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
        db.session.commit()
        return make_response(jsonify({'result': True, 'message': 'Updated existing commute.'}))
    else:
        newCommute: Commute = Commute(
            email=request.json['token']['email'],
            arrival=request.json['content']['arrival'],
            departure=request.json['content']['departure'],
            method=request.json['content']['method'],
            distance=request.json['content']['distance']
        )
        db.session.add(newCommute)
        db.session.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new commute.'}))


# ----- Journal Functions


@app.route('/api/journal', methods=['POST'])
def getJournal():
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
        db.cast(JournalEntry.created,
                db.Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
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
def postJournal():
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
        db.session.commit()
        return make_response(
            jsonify({
                'result': True,
                'message': 'Updated existing journal entry.'
            })
        )
    else:
        newJournal: JournalEntry = JournalEntry(
            email=request.json['token']['email'],
            created=request.json['metadata']['timestamp'],
            title=request.json['content']['title'],
            content=request.json['content']['contents']
        )
        db.session.add(newJournal)
        db.session.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new journal entry.'}))


# ----- Water Functions
@app.route('/api/water', methods=['POST'])
def getWater():
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
        db.cast(WaterCups.date, db.Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
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
def postWater():
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
        db.session.commit()
        return make_response(jsonify({'result': True, 'message': 'Updated existing water entry.'}))
    else:
        newWater: WaterCups = WaterCups(
            email=request.json['token']['email'],
            date=request.json['metadata']['timestamp'],
            count=request.json['content']['cups']
        )
        db.session.add(newWater)
        db.session.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new water entry.'}))


# ----- Shower Functions
@app.route('/api/showers', methods=['POST'])
def getShower():
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
        db.cast(ShowerUsage.date, db.Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
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
def postShower():
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
        db.session.commit()
        return make_response(jsonify({'result': True, 'message': 'Updated existing shower entry.'}))
    else:
        newShower: ShowerUsage = ShowerUsage(
            email=request.json['token']['email'],
            date=request.json['metadata']['timestamp'],
            minutes=request.json['content']['minutes'],
            cold=request.json['content']['cold']
        )
        db.session.add(newShower)
        db.session.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new shower entry.'}))


# ----- Entertainment Functions
@app.route('/api/entertainment', methods=['POST'])
def getEntertainment():
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
        db.cast(EntertainmentUsage.date,
                db.Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
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
def postEntertainment():
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
        db.session.commit()
        return make_response(
            jsonify({
                'result': True,
                'message': 'Updated existing entertainment entry.'
            })
        )
    else:
        newEntertainment: EntertainmentUsage = EntertainmentUsage(
            email=request.json['token']['email'],
            date=request.json['metadata']['timestamp'],
            hours=request.json['content']['hours'],
        )
        db.session.add(newShower)
        db.session.commit()
        return make_response(
            jsonify({
                'result': True,
                'message': 'Inserted new entertainment entry.'
            })
        )


# ----- Health Functions
@app.route('/api/health', methods=['POST'])
def getHealth():
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
        db.cast(Health.date, db.Date) == datetime.strptime(request.json['date'], "%Y-%m-%d"),
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
def postHealth():
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
        db.session.commit()
        return make_response(jsonify({'result': True, 'message': 'Updated existing health entry.'}))
    else:
        newHealth: Health = Health(
            email=request.json['token']['email'],
            date=request.json['metadata']['timestamp'],
            cigarettes=request.json['content']['cigarettes'],
        )
        db.session.add(newShower)
        db.session.commit()
        return make_response(jsonify({'result': True, 'message': 'Inserted new health entry.'}))


# ----- Utility Functions


def check_token(token: Dict[str, str]):
    # TODO: Token expiry
    newHash = hashlib.sha256(
        (token['expiry'] + token['email'] + app.config['SECRET_KEY']).encode('utf-8')
    ).hexdigest()

    return (
        token['hash'] == newHash,
        make_response(jsonify({
            'result': False,
            'message': f'Invalid Token Hash: {newHash}'
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
