import os
import logging
from app import app
from flask import Flask, request, abort, jsonify, make_response
from flask import render_template, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy, DeclarativeMeta
from json import JSONEncoder

log = logging.getLogger(__name__)

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

class ProductJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            return obj.to_dict()
        return super(ProductJSONEncoder, self).default(obj)

app.json_encoder = ProductJSONEncoder

user = 'ubuntu'
password = 'cs207password'
host = 'localhost'
port = '5432'
db = 'ubuntu'
url = 'postgresql://{}:{}@{}:{}/{}'
# Posgres uri
potgres_uri = url.format(user, password, host, port, db)
# SQlite uri
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/tasks.db'
db = SQLAlchemy(app)
db.create_all()


class Task(db.Model):
    __tablename__ = 'tasks'

    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.task_id

    def to_dict(self):
        return dict(action=self.action, task_id=self.task_id)

@app.route('/home', methods=['GET'])
def get_home_spa():
    log.info('Getting Home html')
    return send_from_directory('static', os.path.join('html', 'home.html'))

@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    log.info('Getting all Tasks')
    return jsonify(dict(tasks=Task.query.all()))


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task_by_id(task_id):
    task = Task.query.filter_by(task_id=task_id).first()
    if task is None:
        log.info('Failed to get Task with task_id=%s', task_id)
        abort(404)
    log.info('Getting Task with task_id=%s', task_id)
    return jsonify({'task': task})


@app.route('/tasks', methods=['POST'])
def create_task():
    if not request.json or 'action' not in request.json:
        abort(400)
    log.info('Creating Task with action=%s', request.json['action'])
    prod = Task(action=request.json['action'])
    db.session.add(prod)
    db.session.commit()
    return jsonify({'op': 'OK', 'task': prod}), 201


@app.route('/tasks/<int:task_id>', methods=['PUT', 'POST', 'OPTIONS'])
def update_task(task_id):
    if not request.json or 'action' not in request.json:
        log.info('Could not update. Invalid params')
        abort(400)

    task = Task.query.filter_by(task_id=task_id).first()
    if task is None:
        log.info('Could not find Task id=%s to update', task_id)
        abort(404)

    action = request.json['action']
    log.info('Updating Task id=%s with action %s', task_id, action)
    task.action = action
    db.session.commit()
    return jsonify({'op': 'OK', 'task': task}), 201


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def remove_task(task_id):
    task = Task.query.filter_by(task_id=task_id).first()
    if task is None:
        abort(404)

    log.info('Deleting Task with id=%s', task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'op': 'OK'})


@app.route('/tasks', methods=['DELETE'])
def remove_all_tasks():
    tasks = Task.query.all()
    for task in tasks:
        db.session.delete(task)

    log.info('Deleted all Tasks!')
    db.session.commit()
    return jsonify({'op': 'OK'})


@app.route('/static/<string:directory>/<path:path>')
def send_static(directory, path):
    log.info('Static File Dir:%s, Path:%s', directory, path)
    return send_from_directory('static', os.path.join(directory, path))

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
