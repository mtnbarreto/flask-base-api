# project/api/views.py

from flask import Flask, Blueprint, jsonify, request, render_template

from project.models.models import User
from project import db
from sqlalchemy import exc, or_

from project.api.common.utils import authenticate


users_blueprint = Blueprint('users', __name__, template_folder='../templates/users')

# @users_blueprint.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         db.session.add(User(username=username, email=email))
#         db.session.commit()
#     users = User.query.order_by(User.created_at.desc()).all()
#     return render_template('index.html', users=users)

@users_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

@users_blueprint.route('/users', methods=['POST'])
@authenticate
def add_user(user_id):
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')

    try:
        user = User.first(or_(User.username == username, User.email == email))
        if not user:
            userModel = User(username=username, email=email, password=password)
            db.session.add(userModel)
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{email} was added!'
            }
            return jsonify(response_object), 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'Sorry. That email or username already exists.'
            }
            return jsonify(response_object), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400


@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get single user details"""
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    try:
        user = User.get(id=int(user_id))
        if not user:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                  'username': user.username,
                  'email': user.email,
                  'created_at': user.created_at
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404



@users_blueprint.route('/users', methods=['GET'])
def get_all_users():
    """Get all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    users_list = []
    for user in users:
        user_object = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        }
        users_list.append(user_object)
    response_object = {
        'status': 'success',
        'data': {
            'users': users_list
        }
    }
    return jsonify(response_object), 200
