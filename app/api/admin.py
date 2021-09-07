from logging import error
from flask.json import jsonify
from app.utils import is_json, admin_required
from flask import Blueprint, request

from .. import db

admin = Blueprint('admin', __name__)


# route to assign manager to user
@admin.route('/assign-manager', methods=['POST'])
@admin_required()
def assign_manager():
    is_json(request)

    # check all the fields have been filled
    manager_username = request.json.get('manager_username')
    simple_user_username = request.json.get('simple_user_username')

    if manager_username is None or simple_user_username is None:
        return jsonify(error="All fields are required")

    manager = db.users.find_one({"username": manager_username})

    # check if manager exists
    if not manager or manager.get('role') != 'manager':
        return jsonify({
            "msg": f"No manager found with id: {manager_username}"
        })

    user = db.users.find_one({"username": simple_user_username})

    if user.get('role') != 'simple_user':
        return jsonify(msg="Not a user")

    # check if user exists
    if not user:
        return jsonify({
            "msg": f"No user found with id: {simple_user_username}"
        })

    # if it's the first manager to be assigned
    if user.get('manager_assigned') is None:
        db.users.update_one({"username": simple_user_username}, {
                        '$set': {"manager_assigned": [db.users.find_one({"username": manager_username}).get('user_id')]}})
        return jsonify(msg="manager assigned")


    # if the manager is already assigned then return
    manager_list = user.get('manager_assigned')
    if db.users.find_one({"username": manager_username}).get('user_id') in manager_list:
        return jsonify(msg="manager is already assigned")
    
    # append the new manager to the list of assigned managers
    manager_list.append(str(db.users.find_one(
        {"username": manager_username}).get('user_id')))

    # update the manager assigned list
    db.users.update_one({"username": simple_user_username}, {
                        '$set': {"manager_assigned": manager_list}})

    return jsonify(msg="manager assigned!")


# unassign manager route
@admin.route('/unassign-manager', methods=['POST'])
@admin_required()
def unassign_manager():
    is_json(request)
    
    # get the manager and user id
    manager_id = request.json.get('manager_id')
    simple_user_id = request.json.get('simple_user_id')
    
    if manager_id is None or simple_user_id is None:
        return jsonify(error="All fields required!")
    
    manager = db.users.find_one({"user_id": manager_id})
    
    # check if the token is of manager or if the manager is None
    if manager is None or manager.get('role') != 'manager':
        return jsonify(msg="No manager found")
    
    user = db.users.find_one({"user_id": simple_user_id})
    
    # check if the token is of user or if the user is None
    if user is None or user.get('role') != 'simple_user':
        return jsonify(msg="No user found")
    
    # update the manager assigned list
    if manager_id in user.get('manager_assigned'):
        managers_list = user.get('manager_assigned')
        managers_list.remove(manager_id)
        db.users.update_one({"user_id": simple_user_id}, {'$set': {"manager_assigned": managers_list}})
        db.tasks.delete_many({"assigned_by": manager.get('username')})
    
    return jsonify(msg="manager unassigned")
    
    
    
#  view all tasks
@admin.route('/all-tasks', methods=['GET'])
@admin_required()
def all_tasks():
    data_list = []
    for data in db.tasks.find():
        data_list.append({
            "task_id": data.get('task_id'),
            "task_assigned": data.get('task_assigned'),
            "assigned_by": data.get('assigned_by'),
            "assigned_to": db.users.find_one({"user_id": data['simple_user_id']}).get('username')
        })
        
    if len(data_list) < 1:
        return jsonify(msg="No task to show")
        
    return jsonify(data_list)