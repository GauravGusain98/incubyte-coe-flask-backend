from flask import Flask, jsonify
from flask_restx import Api
from coe.api.routes import api_bp 
from coe.api.user.routes import user_api 
from coe.api.task.routes import task_api 
from coe.models.base import db
from config import Config
from werkzeug.exceptions import Unauthorized

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    api = Api(
        app,
        version="1.0",
        title="COE APP",
        doc="/docs" 
    )

    api.add_namespace(api_bp, path="/")
    api.add_namespace(user_api, path="/user")
    api.add_namespace(task_api, path="/task")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
