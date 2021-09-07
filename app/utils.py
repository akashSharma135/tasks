from flask import jsonify
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from . import db

def is_json(req):
    if not req.json:
        return jsonify(msg="Not a json object"), 500
    
def hash_pwd(pwd):
    return pbkdf2_sha256.hash(pwd)

# verifies the password
def verify_pwd(password, password_in_db):
    return pbkdf2_sha256.verify(password, password_in_db)

# insert task
def insert_task(id, task, identity, simple_user_id):
    db.tasks.insert_one({
        "task_id": id,
        "task_assigned": task,
        "assigned_by": db.users.find_one({"user_id": identity}).get('username'),
        "simple_user_id": simple_user_id,
        "task_status": 'not completed'
    })

# verify admin
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt()
            if db.users.find_one({"user_id": identity["sub"]}).get('role') == 'admin':
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403

        return decorator

    return wrapper

# verify manager
def manager_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt()
            if db.users.find_one({"user_id": identity["sub"]}).get('role') == 'manager':
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403

        return decorator

    return wrapper

# verify admin or manager
def admin_manager_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt()
            if db.users.find_one({"user_id": identity["sub"]}).get('role') == 'admin' or db.users.find_one({"user_id": identity["sub"]}).get('role') == 'manager':
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="You are not manager or admin!"), 403

        return decorator

    return wrapper

def admin_user_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt()
            print(identity)
            if db.users.find_one({"user_id": identity["sub"]}).get('role') == 'admin' or db.users.find_one({"user_id": identity["sub"]}).get('role') == 'simple_user':
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="You are not user or admin!"), 403

        return decorator

    return wrapper