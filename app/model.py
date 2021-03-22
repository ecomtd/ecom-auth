from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class UserCredentials(BaseModel):
    login: EmailStr = Field(title="EMail пользователя")
    password: str = Field(title="Пароль", min_length=8, max_length=255)
    fingerprint: str = Field(title="Отпечаток клиентского приложения", max_length=255)


class Fingerprint(BaseModel):
    fingerprint: str = Field(title="Отпечаток клиентского приложения", max_length=255)


class JWTToken(BaseModel):
    access_token: str = Field(title="Token для доступа к сервисам")
    token_type: str = Field(title="Тип токена")


class ErrorMessage(BaseModel):
    code: Optional[int] = Field(
        None, title="Код ошибки"
    )
    message: str = Field(
        None, title="Текст с описанием ошибки", max_length=255
    )
