from flask.json import jsonify
from flask_jwt_extended.utils import get_jwt_identity
from pymongo.message import insert
from app.utils import admin_manager_required, is_json, admin_user_required, insert_task
from flask import Blueprint, request
from app.utils import is_json
import uuid
from .. import db

task = Blueprint('task', __name__)



# Task assign route for manager and admin
@task.route('/assign-task', methods=['POST'])
@admin_manager_required()
def assign_task():
    is_json(request)
    
    simple_user_id = request.json.get('simple_user_id', None)
    task = request.json.get('task', None)
    
    # check all fields are filled or not
    if simple_user_id is None or task is None:
        return jsonify(error="All fields required!")
    
    identity = get_jwt_identity()
    
    simple_user = db.users.find_one({"user_id": simple_user_id})
    if simple_user is None:
            return jsonify(msg="user does not exists")
        
    if not simple_user.get('role') == 'simple_user':
        return jsonify(msg="Not a user")
    
    if not simple_user:
        return jsonify(msg="user does not exists")
    
    if db.users.find_one({"user_id": identity}).get('role') == 'admin':
        insert_task(str(uuid.uuid4()), task, identity, simple_user_id)
        return jsonify(msg="task assigned")
        
    if simple_user.get('manager_assigned') is None:
        return jsonify(msg="No manager assigned")
    
    if identity not in simple_user.get('manager_assigned'):
        return jsonify(msg="manager not assigned to the user")
    
    insert_task(str(uuid.uuid4()), task, identity, simple_user_id)
    return jsonify(msg="task_assigned")
        
        
    
    


# delete task route only by admin or associated manager
@task.route('/delete-task', methods=['POST'])
@admin_manager_required()
def delete_task():
    is_json(request)
    
    task_id = request.json.get('task_id', None)
    
    if task_id is None:
        return jsonify(msg="All fields required!")
    
    identity = get_jwt_identity()
    
    if db.tasks.find_one({"task_id": task_id}) is None:
        return jsonify(msg="task does not exists!")
    
    if db.users.find_one({"user_id": identity}).get('role') == 'admin':
        db.tasks.delete_one({"task_id": task_id})
        return jsonify(msg="task deleted")
    
    if db.tasks.find_one({"task_id": task_id}).get('assigned_by') == db.users.find_one({"user_id": identity}).get('username'):
        db.tasks.delete_one({"task_id": task_id})
        return jsonify(msg="task deleted")
    
    return jsonify(msg="You cannot delete the task")


# update task status
@task.route('/task-status', methods=['POST'])
@admin_user_required()
def task_status():
    is_json(request)
    
    task_id = request.json.get('task_id', None)
    task_status = request.json.get('task_status', None)
    
    if not db.tasks.find_one({"simple_user_id": get_jwt_identity()}) and db.users.find_one({"user_id": get_jwt_identity()}).get('role') != 'admin':
        return jsonify(msg="user cannot update the status of this task")
    
    if task_id is None:
        return jsonify(msg="All fields required!")
    
    if not db.tasks.find_one({"task_id": task_id}):
        return jsonify(msg="No task found")
    
    db.tasks.update_one({"task_id": task_id}, {'$set': {"task_status": task_status}})
    
    return jsonify(msg="task status updated")       
    