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
    from ESSBackend.models import AppUser, Token
    if not request.json:
        abort(400)
    if 'email' not in request.json or 'password' not in request.json:
        abort(400)

    user: AppUser = AppUser.query.filter_by(
        email=request.json['email']).first()
    if not user:
        return make_response(jsonify({'error': 'User not found'}))

    if checkpw(request.json['password'].encode('utf-8'),
               user.password_hash.encode('utf-8')):
        now = datetime.utcnow()
        hmac = hashlib.sha256(
            (str(now) + user.email + app.config['SECRET_KEY']).encode('utf-8'))
        newToken: Token = Token(
            email=user.email, created=now, hash=hmac.hexdigest())

        db.session.add(newToken)
        db.session.commit()

        return make_response(
            jsonify({
                'token': newToken.hash,
                'email': newToken.email,
                'created': newToken.created
            }))
    else:
        return make_response(jsonify({'error': 'Incorrect Password'}))


@app.route('/api/register', methods=['POST'])
def register():
    from ESSBackend.models import AppUser
    if not request.json:
        abort(400)
    if 'email' not in request.json or 'password' not in request.json:
        abort(400)

    user: AppUser = AppUser.query.filter_by(
        email=request.json['email']).first()
    if user:
        return make_response(jsonify({'error': 'User already exists'}))

    pwhash = (hashpw(request.json['password'].encode('utf-8'),
                     gensalt())).decode('utf-8')
    newUser: AppUser = AppUser(
        password_hash=pwhash, email=request.json['email'])
    db.session.add(newUser)
    db.session.commit()

    return make_response(jsonify({'Status': 'User Successfully Registered'}))


@app.route('/api/logout', methods=['POST'])
def logout():
    from ESSBackend.models import Token
    if not request.json:
        abort(400)
    if 'token' not in request.json:
        abort(400)
    if not check_token(request.json['token']):
        return make_response(jsonify({'Error': 'Invalid Token'}))
    else:
        Token.query.filter_by(hash=request.json['token']).delete()
        db.session.commit()
        return make_response(jsonify({'Status': 'Logged out'}))


# ----- Utility Functions


def check_token(token):
    from ESSBackend.models import Token

    # TODO: Token expiry?

    tokens: List[Token] = [
        hashlib.sha256((str(token.created) + token.email +
                        app.config['SECRET_KEY']).encode('utf-8')).hexdigest()
        for token in Token.query.filter_by(hash=token)
    ]

    return token in tokens


# def require_token(func):
#     from models import Token
#     if check_token(token, email):
#         return make_response(jsonify({'error': 'Invalid Token'}))
#     else:
#         return func


# ----- Error Handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    app.run(debug=app.config['DEBUG'])


if __name__ == '__main__':
    main()
