from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Depends, Cookie
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_403_FORBIDDEN
import hashlib
import app.settings as settings
from app.token import create
from app.database import get_db_cursor, handle_database_exception, check_if_error
from app.model import JWTToken, UserCredentials, ErrorMessage, Fingerprint

tags_metadata = [
    {
        "name": "Auth",
        "description": "Операции по управлению аутентификацией и авторизацией",
    }
]

app = FastAPI(
    title="E-COM PORTAL Auth API",
    openapi_tags=tags_metadata,
    version="0.1.0",
    debug=True,
    root_path=settings.api_path
)


@app.post("/login", response_model=JWTToken, tags=["Auth"],
          summary="Авторизация в системе",
          description="Авторизация пользователя в системе по email и паролю",
          response_description="При успешной авторизации возвращается token-ы, "
                               "которыг могут использоваться для доступа к API",
          responses={403: {"model": ErrorMessage,
                           "description": "При неуспешной авторизации возвращается информация об ошибке  \n\n"
                           "Тип ошибки может быть определён значением атрибута **code**  \n"
                           "Возможные значения:  \n"
                           "- **1**: ошибка авторизации, информация в **message**  \n"
                           "- **2**: срок действия пароля истёк, требуется его смена"}})
async def auth_login(usercredentials: UserCredentials, cursor=Depends(get_db_cursor)):
    if len(usercredentials.password) < 8:
        return JSONResponse(status_code=HTTP_403_FORBIDDEN,
                            content=jsonable_encoder(ErrorMessage(code=1,
                                                                  message="Пароль должен быть не менее 8 символов")))
    try:
        cursor.execute("select * from auth.login(%s,%s,%s)",
                       (usercredentials.login,
                        hashlib.sha512(usercredentials.password.encode('utf-8')).hexdigest(),
                        usercredentials.fingerprint))
        res = cursor.fetchone()
        print(res)
        if res["user_id"]:
            if res["user_id"] < 0:
                return JSONResponse(status_code=HTTP_401_UNAUTHORIZED,
                                    content=jsonable_encoder(ErrorMessage(code=2, message=res["error_message"])))
            else:
                j = JSONResponse(content=jsonable_encoder(
                    JWTToken(access_token=create({"iss": settings.api_domain,
                                                  "sub": res["user_id"],
                                                  "name": res["user_name"],
                                                  "exp": res["access_token_lifetime"],
                                                  "customer_code": res["customer_code"],
                                                  "customer_name": res["customer_name"],
                                                  "services": res["services"]}),
                             token_type="Bearer")
                ))
                j.set_cookie(key="refresh_token",
                             value=res["refresh_token"],
                             httponly=True,
                             domain=settings.api_domain,
                             path=settings.api_path,
                             secure=True)
                return j
        else:
            return JSONResponse(status_code=HTTP_403_FORBIDDEN,
                                content=jsonable_encoder(ErrorMessage(code=1, message=res["error_message"])))
    except Exception as exc:
        return check_if_error(handle_database_exception(cursor.connection, exc))


@app.post("/logout", response_class=Response, tags=["Auth"],
          summary="Выход из системы",
          description="Завершение сессии пользователя в системе",
          response_description="Завершение сессии выполнено успешно",
          responses={401: {"model": ErrorMessage,
                           "description": "Токен пользовательской сессии не действителен"}})
async def logout(refresh_token: Optional[str] = Cookie(None), cursor=Depends(get_db_cursor)):
    try:
        if refresh_token:
            cursor.execute("select * from auth.logout(%s)", (refresh_token, ))
            res = cursor.fetchone()
            if res["logout_succeeded"]:
                return Response(status_code=HTTP_200_OK)
            else:
                return JSONResponse(status_code=HTTP_401_UNAUTHORIZED,
                                    content={"message": "Пользователь не авторизован"})
        else:
            return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"message": "Пользователь не авторизован"})
    except Exception as exc:
        return check_if_error(handle_database_exception(cursor.connection, exc))


@app.post("/refresh_tokens", response_model=JWTToken, tags=["Auth"],
          summary="Обновление токенов",
          description="Получение новых токенов используя refresh token",
          response_description="При успешной авторизации возвращается новые token-ы, "
                               "которыг могут использоваться для доступа к API",
          responses={401: {"model": ErrorMessage,
                           "description": "Токен пользовательской сессии не действителен"}})
async def refresh_tokens(fingerprint: Fingerprint, refresh_token: Optional[str] = Cookie(None),
                         cursor=Depends(get_db_cursor)):
    print("now =", datetime.now())
    print("refresh_token =", refresh_token)
    print("fingerprint = ", fingerprint)
    try:
        if refresh_token:
            cursor.execute("select * from auth.refreshtokens(%s,%s)", (refresh_token, fingerprint.fingerprint))
            res = cursor.fetchone()
            print(res)
            if res["user_id"]:
                j = JSONResponse(content=jsonable_encoder(
                    JWTToken(access_token=create({"iss": settings.api_domain,
                                                  "sub": res["user_id"],
                                                  "name": res["user_name"],
                                                  "exp": res["access_token_lifetime"],
                                                  "customer_code": res["customer_code"],
                                                  "customer_name": res["customer_name"],
                                                  "services": res["services"]}),
                             token_type="Bearer")
                ))
                j.set_cookie(key="refresh_token",
                             value=res["refresh_token"],
                             httponly=True,
                             domain=settings.api_domain,
                             path=settings.api_path,
                             secure=True)
                return j
            else:
                return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"message": res["error_message"]})
        else:
            return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"message": "Пользователь не авторизован"})
    except Exception as exc:
        return check_if_error(handle_database_exception(cursor.connection, exc))
