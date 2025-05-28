from flask import Blueprint, request, make_response, jsonify
from pydantic import ValidationError
from coe.services.user_service import login_user 
from config import Config as settings
from coe.models.base import db
from coe.schemas.user import UserLogin, ErrorResponse, UserLoginResponse

user_api = Blueprint('user_api', __name__, url_prefix="/user")

@user_api.route('/login', methods=['POST'])
def login():
    try:
        # Validate incoming JSON using Pydantic
        user_data = UserLogin.model_validate(request.json)
    except ValidationError as e:
        # Return validation errors with 422 status code (Unprocessable Entity)
        return jsonify({"detail": e.errors()}), 422

    # Call your login function with validated data
    token_data = login_user(user_data, db.session)  # Adjust as per your logic

    if not token_data:
        # Return 401 Unauthorized JSON error response
        error_response = ErrorResponse(detail="Invalid email or password")
        return jsonify(error_response.model_dump(by_alias=True)), 401

    # Build response
    response_body = UserLoginResponse(
        message="User authenticated successfully",
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_type=token_data["token_type"],
    )
    
    response = make_response(jsonify(response_body.model_dump(by_alias=True)))
    
    # Set cookies on the response
    response.set_cookie(
        "access_token",
        token_data["access_token"],
        httponly=True,
        secure=True,
        samesite="None",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        token_data["refresh_token"],
        httponly=True,
        secure=True,
        samesite="None",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        path="/user/token/refresh",
    )

    return response