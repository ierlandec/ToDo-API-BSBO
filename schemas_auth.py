from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from models.user import UserRole


# Схема регистрации нового пользователя
class UserCreate(BaseModel):
    nickname: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Никнейм пользователя",
    )
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Пароль (минимум 6 символов)",
    )


# Схема для входа
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Схема ответа с информацией о пользователе
class UserResponse(BaseModel):
    id: int
    nickname: str
    email: str
    role: str

    class Config:
        from_attributes = True


# Схема ответа с токеном
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Данные, извлекаемые из токена
class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=72)

    @field_validator("new_password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Пароль должен занимать не более 72 байт в UTF-8")
        return value


class AdminUserResponse(UserResponse):
    tasks_count: int
