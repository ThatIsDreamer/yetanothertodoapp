from flask import Flask
from flask_restful import Resource, Api
from data import db_session
from data.tasks import Task

app = Flask(__name__)
api = Api(app)

class TaskApi(Resource):
    def post(self, id):
        # URL parameters are received as function arguments
        db_sess = db_session.create_session()
        task = db_sess.query(Task).filter(Task.id == id).first()
        if task:
            task.status = not task.status
            db_sess.commit()

        return {
            "status": "okie-dokie"
        }, 200


