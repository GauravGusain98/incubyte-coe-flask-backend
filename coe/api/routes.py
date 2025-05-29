from flask_restx import Namespace, Resource
from .swagger_models import define_swagger_models
from coe.schemas.generic import HelloResponse

api_bp = Namespace('Generic', description='Generic routes', path='/')

hello_response_model = define_swagger_models(api_bp)

@api_bp.route('hello')
class Hello(Resource):
    @api_bp.response(200, "Success", hello_response_model)
    def get(self):
        response = HelloResponse(
            message="Hello from Flask COE App!"
        )
        return response