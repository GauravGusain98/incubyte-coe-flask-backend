from flask_restx import fields
from types import SimpleNamespace

def define_user_models(api):
    models = SimpleNamespace()

    models.login_request_model = api.model("LoginRequest", {
        "email": fields.String(required=True, description="User's email"),
        "password": fields.String(required=True, description="User's password")
    })

    models.create_user_request_model = api.model("CreateUserRequest", {
        "first_name": fields.String(required=True, description="User's First Naem"),
        "last_name": fields.String(required=True, description="User's Last Name"),
        "email": fields.String(required=True, description="User's email"),
        "password": fields.String(required=True, description="User's password")
    })

    models.login_response_model = api.model("LoginResponse", {
        "message": fields.String(description="Login status message"),
        "access_token": fields.String(description="JWT access token"),
        "refresh_token": fields.String(description="JWT refresh token"),
        "token_type": fields.String(description="Type of token, usually 'Bearer'")
    })

    models.error_model = api.model("ErrorResponse", {
        "detail": fields.String(description="Error detail/message")
    })

    models.refresh_token_response_model = api.model("RefreshTokenResponse", {
        "message": fields.String(description="Refresh success message"),
        "access_token": fields.String(description="New JWT access token")
    })

    models.user_register_response_model = api.model("UserRegisterResponse", {
        "message": fields.String(description="Registration status"),
        "id": fields.Integer(description="ID of newly registered user")
    })
    
    models.generic_response = api.model("GenericResponse", {
        "message": fields.String(description="Success response message"),
    })

    models.update_user_data_model = api.model("UpdateUserRequest", {
        "first_name": fields.String(description="Updated first name"),
        "last_name": fields.String(description="Updated last name"),
        "email": fields.String(description="Updated email address"),
        "password": fields.String(description="Updated password"),
    })

    models.logged_in_user_response_model = api.model("LoggedInUserResponse", {
        "id": fields.Integer(description="User ID"),
        "first_name": fields.String(description="User's first name"),
        "last_name": fields.String(description="User's last name"),
        "email": fields.String(description="User's email address"),
    })

    return models
