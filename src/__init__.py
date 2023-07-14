from flask import Flask, jsonify
import os
from .auth import auth
from .bookmarks import bookmarks
from .database import db

from flask_jwt_extended import JWTManager

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)

  if test_config is None:
    app.config.from_mapping(
      SECRET_KEY=os.environ.get('SECRET_KEY'),
      SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DB_URI'),
      SQLALCHEMY_ECHO=os.environ.get('SQLALCHEMY_ECHO'),
      SQLALCHEMY_TRACK_MODIFICATIONS=os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS'),
      JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY'),
      JWT_TOKEN_LOCATION = os.environ.get('JWT_TOKEN_LOCATION')
    )

  else:
    app.config.from_mapping(test_config)

  # db.app = app
  db.init_app(app)
  JWTManager(app)
  app.register_blueprint(auth)
  app.register_blueprint(bookmarks)
  return app

