from flask import Blueprint, jsonify
from flask_restx import Namespace, Resource

task_api = Namespace('/task', description='Task related operations')
