from flask import Flask
from app.db import connect_db
from flask_jwt_extended import JWTManager


db = connect_db()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'dd3ff1e5d693dda7482aa5f6e982da03'
    
    jwt = JWTManager(app)
    
    from app.api.admin import admin
    from app.api.manager import manager
    from app.api.simple_user import simple_user
    from app.api.auth import auth
    from app.api.task import task
    from app.api.view import view
    
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/')
    app.register_blueprint(manager, url_prefix='/')
    app.register_blueprint(simple_user, url_prefix='/')
    app.register_blueprint(task, url_prefix='/')
    app.register_blueprint(view, url_prefix='/view')
    
    return app