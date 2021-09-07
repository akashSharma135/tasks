from flask.json import jsonify, request
from app.utils import is_json, hash_pwd, verify_pwd
from flask import Blueprint
from flask_jwt_extended import create_access_token
from .. import db
import uuid

auth = Blueprint('auth', __name__)

# signup route
@auth.route('/signup', methods=['POST'])
def signup():
    is_json(request)
    
    username = request.json.get('username', None)
    name = request.json.get('name', None)
    phone_no = request.json.get('phone_no', None)
    address = request.json.get('address', None)
    password = request.json.get('password', None)
    role = request.json.get('role', None)
    
    if username is None or name is None or phone_no is None or address is None or password is None or role is None:
        return jsonify(error="All fields are required!"), 500
    
    if db.users.find_one({"username": username}):
        return jsonify(error="user already exists")
    
    db.users.insert_one({
        "user_id": str(uuid.uuid4()),
        "username": username,
        "name": name,
        "phone_no": phone_no,
        "address": address,
        "password": hash_pwd(password),
        "role": role
    })
    
    return jsonify(success="account created!"), 200
    
    
# signin route
@auth.route('/signin', methods=['POST'])
def signin():
    is_json(request)
    
    username = request.json.get('username')
    password = request.json.get('password')
    
    if username is None or password is None:
        return jsonify(error="All fields are required!"), 500
    
    # find the user in db
    user = db.users.find_one({"username": username})
    
    # if user exists
    if not user:
        return jsonify(msg="user does not exists!")
    
    # verifies password
    if not verify_pwd(password, user.get('password')):
        return jsonify(error="wrong password!")
    
    # Generating the access token with identity = id
    return jsonify(access_token=create_access_token(user.get('user_id'))), 200