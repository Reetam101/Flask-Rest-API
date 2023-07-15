from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED
import validators
from .database import User, db
from flasgger import swag_from
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, set_access_cookies, set_refresh_cookies


auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post('/register')
def register():
  username = request.json['username']
  email = request.json['email']
  password = request.json['password']

  if len(password) < 6:
    return jsonify({ 'error': "password is too short" }), HTTP_400_BAD_REQUEST
  
  if len(username) < 3:
    return jsonify({'error': "Username is too short"}), HTTP_400_BAD_REQUEST
    
  if not username.isalnum() or " " in username:
    return jsonify({'error': "Username should be alphanumeric, and should not have spaces"}), HTTP_400_BAD_REQUEST
    
  if not validators.email(email):
    return jsonify({'error': 'Email is not valid!'}), HTTP_400_BAD_REQUEST

  if User.query.filter_by(email=email).first() is not None:
    return jsonify({'error': 'Email already exists'}), HTTP_409_CONFLICT
  if User.query.filter_by(username=username).first() is not None:
    return jsonify({'error': 'Username already exists'}), HTTP_409_CONFLICT

  pwd_hash = generate_password_hash(password)
  user = User(username=username, password=pwd_hash, email=email)
  
  db.session.add(user)
  db.session.commit()
  print(user)
  print(type(user))
  return jsonify({
    'message': 'User created successfully'
  }), HTTP_201_CREATED
  

@auth.post("/login")
@swag_from('./docs/auth/login.yaml')
def login():
  email = request.json.get('email', '')
  password = request.json.get('password', '')
  
  user = User.query.filter_by(email=email).first()
  
  if user:
    is_pass_correct = check_password_hash(user.password, password)
    
    if is_pass_correct:
      refresh_token = create_refresh_token(identity=user.id)
      access_token = create_access_token(identity=user.id)
      response = jsonify({
        'user': {
          'refresh_token': refresh_token,
          'access_token': access_token,
          'username': user.username,
          'email': user.email
        }
      })
      # set_access_cookies(response, access_token)
      # set_refresh_cookies(response, refresh_token)
      return response
  
  return jsonify({ 'error': "Wrong credentials" }), 401    

@auth.get("/profile")
@jwt_required()
def profile():
  user_id = get_jwt_identity()
  
  user = User.query.filter_by(id=user_id).first()
  
  return jsonify({
    'username': user.username,
    'email': user.email
  }), 200
  
  
@auth.get('/token/refresh')
@jwt_required(refresh=True)
def get_refresh_token():
  user_id = get_jwt_identity()
  access_token = create_access_token(identity=user_id)
  response = jsonify({
    'access_token': access_token
  })
  # set_access_cookies(response, access_token)
  return response, 200
  