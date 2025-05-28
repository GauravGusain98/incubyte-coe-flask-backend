from flask import Flask
from coe.api.routes import api_bp 
from coe.api.user.routes import user_api 
from coe.api.task.routes import task_api 
from coe.models.base import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(user_api)
    app.register_blueprint(task_api)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
