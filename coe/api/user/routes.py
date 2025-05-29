from flask import request, make_response, jsonify
from flask_restx import Namespace, Resource
from pydantic import ValidationError
from coe.services.auth_service import create_access_token, get_current_user, login_required
from coe.services.user_service import login_user, create_user, remove_user, update_user
from config import Config as settings
from coe.models.base import db
from coe.schemas.user import UserLogin, UserLoginResponse, RefreshTokenResponse, UserRegisterResponse, CreateUser, UserLogoutResponse, UserDeleteResponse, UpdateUser, UserUpdateResponse, LoggedInUserResponse
from coe.api.user.swagger_models import define_user_models
from jose import JWTError, jwt

user_api = Namespace('User', description='User related operations', path='user')

swagger_models = define_user_models(user_api)

@user_api.route('/login')
class Login(Resource):
    @user_api.expect(swagger_models.login_request_model)
    @user_api.response(200, "Success", swagger_models.login_response_model)
    @user_api.response(401, "Unauthorized", swagger_models.error_model)
    @user_api.response(422, "Validation Error", swagger_models.error_model)
    def post(self):
        try:
            user_data = UserLogin.model_validate(request.json)
        except ValidationError as e:
            return {"detail": e.errors()}, 422

        token_data = login_user(user_data, db.session)

        if not token_data:
            return {"detail": "Invalid email or password"}, 401

        response_body = UserLoginResponse(
            message="User authenticated successfully",
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
        )

        response = make_response(jsonify(response_body.model_dump(by_alias=True)))

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


@user_api.route("/token/refresh")
class RefreshAccessToken(Resource):
    @user_api.response(200, "Success", swagger_models.refresh_token_response_model)
    @user_api.response(403, "Forbidden", swagger_models.error_model)
    @user_api.response(401, "Unauthorized", swagger_models.error_model)
    @user_api.response(422, "Validation Error", swagger_models.error_model)
    def post(self):
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return {"detail": "Missing refresh token"}, 401

        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            if payload.get("type") != "refresh":
                return {"detail": "Invalid refresh token"}, 403

            new_access_token = create_access_token({"user_id": payload["user_id"]})
            
            result = {"message": "Access token refreshed successfully", "access_token": new_access_token}

            response_object = RefreshTokenResponse.model_validate(result)
            response = make_response(jsonify(response_object.model_dump(by_alias=True)))
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                samesite="None",
                secure=True,
                path="/",
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

            return response
        except JWTError:
            return {"detail": "Invalid refresh token"}, 403
        
@user_api.route("/register")
class Register(Resource):
    @user_api.expect(swagger_models.create_user_request_model)
    @user_api.response(201, "Created", swagger_models.user_register_response_model)
    @user_api.response(400, "Bad Request",swagger_models.error_model)
    def post(self):
        user_data = CreateUser.model_validate(request.json)
        new_user = create_user(user_data, db.session)
        result = {"message": "User registered successfully", "user_id": new_user.id}
        
        response_object = UserRegisterResponse.model_validate(result)
        response = make_response(jsonify(response_object.model_dump(by_alias=True)))
        response.status_code = 201

        return response
    
@user_api.route("/<int:user_id>")
class UserOperation(Resource):
    @login_required
    @user_api.expect(swagger_models.update_user_data_model)
    @user_api.response(200, "Success", swagger_models.generic_response)
    @user_api.response(404, "Not Found", swagger_models.error_model)
    @user_api.response(422, "Validation Error", swagger_models.error_model)
    def put(self, user_id):
        try:
            user_data = UpdateUser.model_validate(request.json)
        except ValidationError as e:
            return {"detail": e.errors()}, 422
        
        success = update_user(user_id, user_data, db.session)
        
        if success:
            result = {"message": "User data updated successfully"}
            response_object = UserUpdateResponse.model_validate(result)
            response = make_response(jsonify(response_object.model_dump(by_alias=True)))
            return response
        else:
            return {"detail": "User not found"}, 404
    
    @login_required
    @user_api.response(200, "Success", swagger_models.generic_response)
    @user_api.response(404, "Not Found", swagger_models.error_model)
    def delete(self, user_id):
        success = remove_user(user_id, db.session)

        if success:
            result = {"message": "User removed successfully"}
            response_object = UserDeleteResponse.model_validate(result)
            response = make_response(jsonify(response_object.model_dump(by_alias=True)))
            return response
        else:
            return {"detail": "User not found"}, 404
    
@user_api.route("/logout")
class Logout(Resource):
    @login_required
    @user_api.response(200, "Success", swagger_models.generic_response)
    def post(self):
        result = {"message": "Logged out successfully"}
        response_object = UserLogoutResponse.model_validate(result)
        response = make_response(jsonify(response_object.model_dump(by_alias=True)))
        response.delete_cookie(
            key="access_token",
            path="/",
            httponly=True,
            secure=True,
            samesite="None"
        )

        response.delete_cookie(
            key="refresh_token",
            path="/user/token/refresh",
            httponly=True,
            secure=True,
            samesite="None"
        )
        return response

@user_api.route("/me")
class GetMe(Resource):
    @login_required
    @user_api.response(200, "Success", swagger_models.logged_in_user_response_model)
    @user_api.response(401, "Unauthorized", swagger_models.error_model)
    def get(self):
        user = get_current_user()

        response_object = LoggedInUserResponse.model_validate(user)
        response = make_response(jsonify(response_object.model_dump(by_alias=True)))
        return response