from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str = ""
    last_name: str = ""
    investor_type: Literal["conservative", "moderate", "aggressive"] = "moderate"

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    investor_type: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshRequest(BaseModel):
    refresh_token: str 
