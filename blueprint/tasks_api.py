import flask
from flask import Blueprint, request, jsonify
from data import db_session
from data.tasks import Task

blueprint = flask.Blueprint(
    'task_api',
    __name__,
    template_folder='templates'
)

@blueprint.route('/toggle/<id>', methods=['POST'])
def toggle(id):
    db_sess = db_session.create_session()
    data = request.get_json()
    print(data)