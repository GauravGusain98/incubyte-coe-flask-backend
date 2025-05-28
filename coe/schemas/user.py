from pydantic import EmailStr, Field, constr, conint
from coe.models.base import CamelModel
from typing import Optional

NameStr = constr(strip_whitespace=True, min_length=1, max_length=50)
PasswordStr = constr(min_length=8, max_length=128)
UserID = conint(gt=0)

### Request Schemas
class CreateUser(CamelModel):
    first_name: NameStr = Field(..., description="First name of the user")
    last_name: NameStr = Field(..., description="Last name of the user")
    email: EmailStr = Field(..., description="User's email address")
    password: PasswordStr = Field(..., description="User's password (8–128 chars)")


class UpdateUser(CamelModel):
    first_name: Optional[NameStr] = Field(None, description="Updated first name")
    last_name: Optional[NameStr] = Field(None, description="Updated last name")
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    password: Optional[PasswordStr] = Field(None, description="Updated password")


class UserLogin(CamelModel):
    email: EmailStr = Field(..., description="User's email for login")
    password: PasswordStr = Field(..., description="User's password")

class RefreshToken(CamelModel):
    refresh_token: str

### Response Schemas
class RefreshTokenResponse(CamelModel):
    access_token: str
    message: str

class UserRegisterResponse(CamelModel):
    message: str
    user_id: int

class UserLoginResponse(CamelModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str

class LoggedInUserResponse(CamelModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

class UserLogoutResponse(CamelModel):
    message: str

class UserUpdateResponse(CamelModel):
    message: str

class UserDeleteResponse(CamelModel):
    message: str

class ErrorResponse(CamelModel):
    detail: str