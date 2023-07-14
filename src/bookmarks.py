from flask import Blueprint, request, jsonify
import validators
from .database import Bookmark, db
from flask_jwt_extended import get_jwt_identity, jwt_required

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def bookmark():
  current_user = get_jwt_identity()
  
  if request.method == 'POST':
    content = request.get_json().get('content', '')
    url = request.get_json().get('url', '')
    
    if not validators.url(url):
      return jsonify({
        'error': 'Enter a valid url'
      }), 400
      
    if Bookmark.query.filter_by(url=url).first():
      return jsonify({
        'error': 'URL already exists'
      }), 409
    
    bookmark = Bookmark(url=url, content=content, user_id=current_user)
    db.session.add(bookmark)
    db.session.commit()
    
    return jsonify({
      'id': bookmark.id,
      'url': bookmark.url,
      'short_url': bookmark.short_url,
      'visits': bookmark.visits,
      'content': bookmark.content,
      'created_at': bookmark.created_at,
      'updated_at': bookmark.updated_at
    }), 201
    
  else:
    # get all bookmarks 
    bookmarks = Bookmark.query.filter_by(user_id=current_user)
    data = []
    for bookmark in bookmarks:
      data.append({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'content': bookmark.content,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at
      })
      
    return jsonify({
      'data': data
    }), 200