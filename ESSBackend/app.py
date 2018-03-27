# RESTful API for our application
# Guided by several online resources:
# - https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

from bcrypt import checkpw, hashpw, gensalt
from ESSBackend.config import Config
from datetime import datetime
from flask import Flask, abort, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy

import hashlib

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)


@app.route('/api/login', methods=['POST'])
def login():
    from ESSBackend.models import AppUser
    if not request.json:
        return make_response(
            jsonify({
                'status': False,
                'message': 'Where\'s the JSON?'
            }))
    if 'email' not in request.json or 'password' not in request.json:
        return make_response(
            jsonify({
                'status': False,
                'message': 'Login requires email and password'
            }))

    user: AppUser = AppUser.query.filter_by(
        email=request.json['email']).first()
    if not user:
        return make_response(
            jsonify({
                'result': False,
                'message': 'User not found'
            }))

    if checkpw(request.json['password'].encode('utf-8'),
               user.password_hash.encode('utf-8')):
        now = datetime.utcnow()
        hmac = hashlib.sha256(
            (str(now) + user.email + app.config['SECRET_KEY']).encode('utf-8'))

        return make_response(
            jsonify({
                'token': {
                    'hash': hmac.hexdigest(),
                    'email': user.email,
                    'expiry': now  # TODO: send actual expiry
                },
                'result': True,
                'message': "Successful login"
            }))
    else:
        return make_response(
            jsonify({
                'result': False,
                'message': 'Incorrect Password'
            }))


@app.route('/api/register', methods=['POST'])
def register():
    from ESSBackend.models import AppUser
    if not request.json:
        return make_response(
            jsonify({
                'status': False,
                'message': 'Where\'s the JSON?'
            }))
    if 'email' not in request.json or 'password' not in request.json:
        return make_response(
            jsonify({
                'status': False,
                'message': 'Registration requires email and password'
            }))

    user: AppUser = AppUser.query.filter_by(
        email=request.json['email']).first()
    if user:
        return make_response(
            jsonify({
                'status': False,
                'message': 'User already exists'
            }))

    pwhash = (hashpw(request.json['password'].encode('utf-8'),
                     gensalt())).decode('utf-8')
    newUser: AppUser = AppUser(
        password_hash=pwhash, email=request.json['email'])
    db.session.add(newUser)
    db.session.commit()

    now = datetime.utcnow()
    hmac = hashlib.sha256(
        (str(now) + user.email + app.config['SECRET_KEY']).encode('utf-8'))

    return make_response(
        jsonify({
            'token': {
                'hash': hmac.hexdigest(),
                'email': user.email,
                'expiry': now  # TODO: send actual expiry
            },
            'result': True,
            'message': 'Successful registration'
        }))


@app.route('/api/status', methods=['GET'])
def status():
    return make_response(
        jsonify({
            'result': True,
            'message': 'Server status normal'
        }))


@app.route('/api/food', methods=['GET'])
def getFood():
    return make_response(
        jsonify({
            'status': False,
            'message': 'Not Implemented'
        }))


@app.route('/api/food', methods=['POST'])
def postFood():
    return make_response(
        jsonify({
            'status': False,
            'message': 'Not Implemented'
        }))


@app.route('/api/commute', methods=['GET'])
def getCommute():
    return make_response(
        jsonify({
            'status': False,
            'message': 'Not Implemented'
        }))


@app.route('/api/commute', methods=['POST'])
def postCommute():
    return make_response(
        jsonify({
            'status': False,
            'message': 'Not Implemented'
        }))


@app.route('/api/journal', methods=['GET'])
def getJournal():
    return make_response(
        jsonify({
            'status': False,
            'message': 'Not Implemented'
        }))


@app.route('/api/journal', methods=['POST'])
def postJournal():
    return make_response(
        jsonify({
            'status': False,
            'message': 'Not Implemented'
        }))


# ----- Utility Functions


def check_token(hash, expiry, email):
    # TODO: Token expiry

    newHash = hashlib.sha256(
        (expiry + email + app.config['SECRET_KEY']).encode('utf-8'))

    return hash == newHash


# ----- Error Handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    app.run(debug=app.config['DEBUG'])


if __name__ == '__main__':
    main()
