from flask import Blueprint
from flask.json import jsonify
from .. import db

view = Blueprint('view', __name__)

# view all users
@view.route('/all-simple-users', methods=['GET'])
def all_simple_users():
    data_list = []
    for data in db.users.find({"role": "simple_user"}):
        data_list.append({
            "id": data['user_id'],
            "username": data['username'],
            "name": data['name'],
            "phone_no": data['phone_no'],
            "address": data['address']
        })
    if len(data_list) < 1:
        return jsonify(msg="No user to show")
    return jsonify(data_list)


# view all managers
@view.route('/all-managers', methods=['GET'])
def all_managers():
    data_list = []
    for data in db.users.find({"role": "manager"}):
        data_list.append({
            "id": data['user_id'],
            "username": data['username'],
            "name": data['name'],
            "phone_no": data['phone_no'],
            "address": data['address']
        })
    if len(data_list) < 1:
        return jsonify(msg="No user to show")
    return jsonify(data_list)