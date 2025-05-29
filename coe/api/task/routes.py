from flask import request, jsonify, make_response
from flask_restx import Namespace, Resource
from pydantic import ValidationError

from coe.models.base import db
from coe.api.task.swagger_models import define_task_models
from coe.services.auth_service import login_required, get_current_user
from coe.services.task_service import (
    create_task, find_task_by_id, update_task_details,
    remove_task, get_tasks_list
)
from coe.schemas.task import (
    CreateTaskRequestSchema, CreateTaskResponseSchema,
    GetTaskResponseSchema, GetTaskListResponseSchema,
    UpdateTaskRequestSchema, UpdateTaskResponseSchema,
    DeleteTaskResponseSchema, TaskFilters, TaskSort
)

import math

task_api = Namespace('Task', path="/task", description='Task related operations', decorators=[login_required])
swagger_models = define_task_models(task_api)

@task_api.route("/add")
class TaskCreate(Resource):
    @task_api.expect(swagger_models.create_task_request)
    @task_api.response(201, "Task Created", swagger_models.create_task_response)
    @task_api.response(401, "Unauthorized", swagger_models.error_response)
    @task_api.response(422, "Validation Error", swagger_models.error_response)
    def post(self):
        try:
            task_data = CreateTaskRequestSchema.model_validate(request.json)
        except ValidationError as e:
            return {"detail": e.errors()}, 422
        
        current_user = get_current_user()
        new_task = create_task(task_data, db.session, current_user)
        result = {"message": "Task created successfully", "task_id": new_task.id}
        
        response_object = CreateTaskResponseSchema.model_validate(result)
        return make_response(jsonify(response_object.model_dump(by_alias=True)), 201)

@task_api.route("/list")
class TaskList(Resource):
    @task_api.param("page", "Page number (starts from 1)", type="integer", required=False)
    @task_api.param("recordsPerPage", "Number of items per page", type="integer", required=False)
    @task_api.param("status", "Filter by task status", type="string", required=False)
    @task_api.param("priority", "Filter by task priority", type="string", required=False)
    @task_api.param("search", "Search for task using name or description text", type="string", required=False)
    @task_api.param("sortBy", "Sort result by field", type="string", required=False)
    @task_api.param("sortOrder", "Sorting Order", type="string", required=False)
    @task_api.response(200, "Success", swagger_models.get_task_list_response)
    @task_api.response(422, "Validation Error", swagger_models.error_response)
    def get(self):
        try:
            page = int(request.args.get("page", 1))
            limit = int(request.args.get("records_per_page", 10))

            filters_data = {
                "status": request.args.get("status"),
                "priority": request.args.get("priority"),
                "search": request.args.get("search")
            }

            sort_data = {
                "sort_by": request.args.get("sortBy"),
                "sort_order": request.args.get("sortOrder")
            }

            filters = TaskFilters(**{k: v for k, v in filters_data.items() if v is not None})
            sort = TaskSort(**{k: v for k, v in sort_data.items() if v is not None})

        except (ValueError, ValidationError) as e:
            return {"detail": str(e)}, 422

        skip = (page - 1) * limit
        tasks, total_records = get_tasks_list(db.session, filters, sort, skip=skip, limit=limit)
        
        result = {
            "message": "Task fetched successfully",
            "tasks": tasks,
            "pagination": {
                "page": page,
                "limit": limit,
                "count": len(tasks),
                "total": total_records,
                "total_pages": math.ceil(total_records / limit) if limit else 1
            }
        }

        response_object = GetTaskListResponseSchema.model_validate(result)
        return make_response(jsonify(response_object.model_dump(by_alias=True, mode="json")), 200)


@task_api.route("/<int:task_id>")
class TaskGet(Resource):
    @task_api.response(200, "Success", swagger_models.get_task_response)
    @task_api.response(404, "Not Found", swagger_models.error_response)
    def get(self, task_id):
        task = find_task_by_id(task_id, db.session)
        if not task:
            return {"detail": "Task not found"}, 404

        response_object = GetTaskResponseSchema.model_validate(task)
        return make_response(jsonify(response_object.model_dump(by_alias=True, mode="json")), 200)

    @task_api.expect(swagger_models.update_task_request)
    @task_api.response(200, "Success", swagger_models.generic_response)
    @task_api.response(404, "Not Found", swagger_models.error_response)
    @task_api.response(422, "Validation Error", swagger_models.error_response)
    def put(self, task_id):
        try:
            task_data = UpdateTaskRequestSchema.model_validate(request.json)
        except ValidationError as e:
            return {"detail": e.errors()}, 422

        success = update_task_details(task_id, task_data, db.session)
        if not success:
            return {"detail": "Task not found"}, 404

        result = {"message": "Task data updated successfully"}
        response_object = UpdateTaskResponseSchema.model_validate(result)
        return make_response(jsonify(response_object.model_dump(by_alias=True)), 200)

    @task_api.response(200, "Success", swagger_models.generic_response)
    @task_api.response(404, "Not Found", swagger_models.error_response)
    def delete(self, task_id):
        success = remove_task(task_id, db.session)
        if not success:
            return {"detail": "Task not found"}, 404

        result = {"message": "Task removed successfully"}
        response_object = DeleteTaskResponseSchema.model_validate(result)
        return make_response(jsonify(response_object.model_dump(by_alias=True)), 200)
