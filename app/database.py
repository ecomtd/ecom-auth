from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST
import app.settings as settings
import psycopg2
from psycopg2 import pool, extras
from fastapi import Depends
from fastapi.logger import logger
from app.models import ErrorMessage

dbpool = psycopg2.pool.ThreadedConnectionPool(settings.db_min_connections, settings.db_max_connections,
                                              user=settings.dbusr, password=settings.dbpwd,
                                              host=settings.dbip, port=settings.dbport, database=settings.dbname)


async def get_db_connection():
    connection = dbpool.getconn()
    bad = False
    try:
        yield connection
        if hasattr(connection, "bad"):
            bad = True
        if not bad:
            connection.commit()
    finally:
        dbpool.putconn(connection, close=bad)


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


def handle_database_exception(connection, exc):
    if type(exc) is psycopg2.errors.RaiseException:  # noqa
        connection.rollback()
        return ErrorMessage(message=str(exc).partition("\n")[0])
    if type(exc) is psycopg2.errors.AdminShutdown:  # noqa
        connection.bad = True
        logger.error(f"Database exception: {exc}")
        return ErrorMessage(message="try later...")
    elif type(exc) is psycopg2.OperationalError:
        connection.bad = True
        logger.error(f"Database exception: {exc}")
        return ErrorMessage(message="try later...")
    else:
        raise exc
