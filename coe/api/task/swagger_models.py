from flask_restx import fields
from types import SimpleNamespace

def define_task_models(api):
    models = SimpleNamespace()

    priority_enum = ['low', 'medium', 'high']
    status_enum = ['pending', 'in_progress', 'completed']
    sort_order_enum = ['asc', 'desc']

    models.pagination = api.model('Pagination', {
        'page': fields.Integer(required=True),
        'limit': fields.Integer(required=True),
        'count': fields.Integer(required=True),
        'total': fields.Integer(required=True),
        'totalPages': fields.Integer(required=True, attribute='total_pages')
    })

    models.get_tasks = api.model('GetTasks', {
        'status': fields.String(enum=status_enum, required=False),
        'priority': fields.String(enum=priority_enum, required=False),
        'search': fields.String(required=False),
        'sortBy': fields.String(required=False, attribute='sort_by'),
        'sortOrder': fields.String(enum=sort_order_enum, required=False, attribute='sort_order')
    })

    models.create_task_request = api.model('CreateTaskRequest', {
        'name': fields.String(required=True, description="First name of the task"),
        'description': fields.String(required=True, description="Description of the task"),
        'assigneeId': fields.Integer(required=False, attribute='assignee_id'),
        'dueDate': fields.Date(required=True, attribute='due_date'),
        'startDate': fields.Date(required=False, attribute='start_date'),
        'priority': fields.String(enum=priority_enum, required=False)
    })

    models.update_task_request = api.model('UpdateTaskRequest', {
        'name': fields.String(required=False),
        'description': fields.String(required=False),
        'assigneeId': fields.Integer(required=False, attribute='assignee_id'),
        'dueDate': fields.Date(required=False, attribute='due_date'),
        'startDate': fields.Date(required=False, attribute='start_date'),
        'priority': fields.String(enum=priority_enum, required=False),
        'status': fields.String(enum=status_enum, required=False)
    })

    models.create_task_response = api.model('CreateTaskResponse', {
        'message': fields.String(),
        'taskId': fields.Integer(attribute='task_id')
    })

    models.generic_response = api.model('GenericResponse', {
        'message': fields.String()
    })

    models.get_task_response = api.model('GetTaskResponse', {
        'id': fields.Integer(),
        'name': fields.String(),
        'description': fields.String(),
        'createdById': fields.Integer(attribute='created_by_id'),
        'assigneeId': fields.Integer(attribute='assignee_id'),
        'dueDate': fields.Date(attribute='due_date'),
        'startDate': fields.Date(attribute='start_date'),
        'priority': fields.String(enum=priority_enum),
        'status': fields.String(enum=status_enum),
        'createdAt': fields.DateTime(attribute='created_at'),
        'updatedOn': fields.DateTime(attribute='updated_on')
    })

    models.get_task_list_response = api.model('GetTaskListResponse', {
        'message': fields.String(),
        'tasks': fields.List(fields.Nested(models.get_task_response)),
        'pagination': fields.Nested(models.pagination)
    })

    models.error_response = api.model('ErrorResponse', {
        'detail': fields.String()
    })

    return models
