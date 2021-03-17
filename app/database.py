import app.settings as settings
import psycopg2
from psycopg2 import pool, extras
from fastapi import Depends


dbpool = psycopg2.pool.ThreadedConnectionPool(settings.db_min_connections, settings.db_max_connections,
                                              user=settings.dbusr, password=settings.dbpwd,
                                              host=settings.dbip, port=settings.dbport, database=settings.dbname)


async def get_db_connection():
    connection = dbpool.getconn()
    try:
        yield connection
        connection.commit()
    except psycopg2.OperationalError as error:
        connection.rollback()
        connection.close()
        raise error
    finally:
        dbpool.putconn(connection)


async def get_db_cursor(connection=Depends(get_db_connection)):
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        yield cursor
    finally:
        cursor.close()
