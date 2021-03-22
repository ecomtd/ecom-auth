from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
import app.settings as settings
import psycopg2
from psycopg2 import pool, extras
from fastapi import Depends
from fastapi.logger import logger
from app.model import ErrorMessage


dbpool = psycopg2.pool.ThreadedConnectionPool(minconn=settings.db_min_connections, maxconn=settings.db_max_connections,
                                              user=settings.dbusr, password=settings.dbpwd,
                                              host=settings.dbip, port=settings.dbport, database=settings.dbname)


async def get_db_connection():
    tries_count = int(settings.db_max_connections)*int(settings.workers_count)
    connection_active = False
    connection = dbpool.getconn()
    while tries_count > 0 and not connection_active:
        try:
            cursor = connection.cursor()
            try:
                cursor.execute("select 1")
                cursor.fetchone()
                connection_active = True
            finally:
                cursor.close()
        except (psycopg2.errors.AdminShutdown, psycopg2.OperationalError) as exc:   # noqa
            dbpool.putconn(connection, close=True)
            logger.error(f"Database connection failed: {exc}")
            logger.error("Reconnecting.....")
            tries_count -= 1
            if tries_count == 0:
                raise
            else:
                connection = dbpool.getconn()
    try:
        yield connection
        if connection.closed == 0:
            connection.commit()
    finally:
        if connection.closed == 0:
            dbpool.putconn(connection)
        else:
            dbpool.putconn(connection, close=True)


async def get_db_cursor(connection=Depends(get_db_connection)):
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        yield cursor
    finally:
        cursor.close()


def check_if_error(obj):
    if type(obj) is ErrorMessage:
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content=jsonable_encoder(obj))
    else:
        return obj


def check_if_empty_list(obj):
    return obj[0] \
        if len(obj) > 0 \
        else JSONResponse(status_code=HTTP_404_NOT_FOUND,
                          content=jsonable_encoder(ErrorMessage(code=404, message="Запрошенный объект не найден")))


def handle_database_exception(connection, exc):
    if type(exc) is psycopg2.errors.RaiseException:  # noqa
        connection.rollback()
        return ErrorMessage(message=str(exc).partition("\n")[0])
    if type(exc) is psycopg2.errors.AdminShutdown:  # noqa
        connection.close()
        logger.error(f"Database exception: {exc}")
        return ErrorMessage(message="try later...")
    elif type(exc) is psycopg2.OperationalError:
        connection.close()
        logger.error(f"Database exception: {exc}")
        return ErrorMessage(message="try later...")
    else:
        raise exc
