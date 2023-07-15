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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 3, type=int)
    bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)
    data = []
    for bookmark in bookmarks.items:
      data.append({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'content': bookmark.content,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at
      })
    
    meta = {
      "page": bookmarks.page,
      "pages": bookmarks.pages,
      "total_count": bookmarks.total,
      "prev": bookmarks.prev_num,
      "next_page": bookmarks.next_num,
      "has_next": bookmarks.has_next,
      "has_prev": bookmarks.has_prev
    }
    return jsonify({
      'data': data,
      'meta': meta
    }), 200
    
    
@bookmarks.get("/<int:id>")
@jwt_required()
def get_single_bookmark(id):
  current_user_id = get_jwt_identity()
  bookmark = Bookmark.query.filter_by(user_id=current_user_id, id=id).first()
  
  if not bookmark:
    return jsonify({
      'message': 'Item not found!'
    }), 404
  
  
  return jsonify({
    'id': bookmark.id,
    'url': bookmark.url,
    'short_url': bookmark.short_url,
    'visits': bookmark.visits,
    'content': bookmark.content,
    'created_at': bookmark.created_at,
    'updated_at': bookmark.updated_at
  }), 200


@bookmarks.put("/<int:id>")
@bookmarks.patch("/<int:id>")
@jwt_required()
def update_bookmark(id):
  current_user_id = get_jwt_identity()
  bookmark = Bookmark.query.filter_by(user_id=current_user_id, id=id).first()
  
  if not bookmark:
    return jsonify({
      'message': 'Item not found!'
    }), 404
  content = request.get_json().get('content', '')
  url = request.get_json().get('url', '')
  if not validators.url(url):
      return jsonify({
        'error': 'Enter a valid url'
      }), 400
      
  bookmark.url = url
  bookmark.content = content
  
  db.session.commit()
  
  return jsonify({
    'message': 'Bookmark updated successfully',
    'id': bookmark.id,
    'url': bookmark.url,
    'short_url': bookmark.short_url,
    'visits': bookmark.visits,
    'content': bookmark.content,
    'created_at': bookmark.created_at,
    'updated_at': bookmark.updated_at
  }), 200
  

@bookmarks.delete("/<int:id>")
@jwt_required()
def delete_bookmark(id):
  current_user_id = get_jwt_identity()
  bookmark = Bookmark.query.filter_by(user_id=current_user_id, id=id).first()
  
  if not bookmark:
    return jsonify({
      'message': 'Item not found!'
    }), 404
  content = request.get_json().get('content', '')
  url = request.get_json().get('url', '')
  if not validators.url(url):
      return jsonify({
        'error': 'Enter a valid url'
      }), 400
  
  db.session.delete(bookmark)
  db.session.commit()
  
  return jsonify({
    'message': 'Bookmark deleted successfully'
  }), 204


@bookmarks.get("/stats")
@jwt_required()
def get_stats():
  data = []
  current_user_id = get_jwt_identity()
  items = Bookmark.query.filter_by(user_id=current_user_id).all()
  
  for item in items:
    new_link = {
      'visits': item.visits,
      'url': item.url,
      'id': item.id,
      'short_url': item.short_url
    }
    data.append(new_link)
  return jsonify({
    'data': data
  }), 200