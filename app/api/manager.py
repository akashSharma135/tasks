from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from app.utils import manager_required
from flask import Blueprint, jsonify
from .. import db

manager = Blueprint('manager', __name__)

# view tasks route
@manager.route('/assigned-tasks')
@jwt_required()
@manager_required()
def assigned_tasks():
    data_list = []
    for data in db.tasks.find({"assigned_by": db.users.find_one({"user_id": get_jwt_identity()}).get('username')}):
        data_list.append({
            "task_id": data['task_id'],
            "task_assigned": data['task_assigned'],
            "assigned_by": data['assigned_by'],
            "assigned_to": db.users.find_one({"user_id": data['simple_user_id']}).get('username')
        })
        
    if len(data_list) < 1:
        return jsonify(msg="No task to show")
        
    return jsonify(data_list)