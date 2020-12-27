import asyncio
import asyncpg
import logging
import psycopg2
import typing
from collections.abc import Iterable

from CustomErrors import ToManyRowsChanged
from config import SECRETS

logger = logging.getLogger('psql')


class SQLRequest:
    def __init__(self, query, parameters, max_changing_rows, ro):
        self.query = query
        self.parameters = parameters
        self.max_changing_rows = max_changing_rows
        self.ro = ro
        self.result = None

    def add_result(self, result):
        self.result = result


async def save_access_async(requests):
    connection = None
    try:
        connection = await asyncpg.connect(host = SECRETS.SQL_Login.host, database = "supporter",
                                           user = SECRETS.SQL_Login.user, password = SECRETS.SQL_Login.passwd)

        async with connection.transaction():

            for request in requests:
                if request.parameters is None:
                    request.parameters = set()

                logger.debug(
                    f'Executing SQL. RO: {request.ro}:\n  "{request.query}"\n  with Parameters: {request.parameters}')

                if not request.ro:
                    # coroutine execute(query: str, *args, timeout: float = None) → str
                    res = await connection.execute(request.query, *request.parameters, timeout = 30.0)
                    rowcount = int(res.split()[-1])
                    if rowcount <= request.max_changing_rows or request.max_changing_rows == -1:
                        request.add_result(rowcount)
                    else:
                        raise ToManyRowsChanged(expected = request.max_changing_rows, received = rowcount)

                else:
                    # coroutine fetch(query, *args, timeout=None, record_class=None) → list
                    rows = await connection.fetch(request.query, *request.parameters, timeout = 30.0)
                    request.add_result(rows)

    except Exception as err:
        raise err
    finally:
        if connection is not None:
            await connection.close()


async def save_write(sql_statement: str, parameters: typing.Optional[Iterable] = None, max_changing_rows=-1):
    r = SQLRequest(sql_statement, parameters, max_changing_rows, False)
    await save_access_async([r])
    return r.result


async def save_read(sql_statement: str, parameters: typing.Optional[Iterable] = None):
    r = SQLRequest(sql_statement, parameters, 0, True)
    await save_access_async([r])
    return r.result


def save_access_sync(requests):
    connection = None
    try:
        connection = psycopg2.connect(host = SECRETS.SQL_Login.host, database = "supporter",
                                      user = SECRETS.SQL_Login.user, password = SECRETS.SQL_Login.passwd)
        cursor = connection.cursor()

        for request in requests:
            logger.debug(
                f'Executing SQL. RO: {request.ro}:\n  "{request.query}"\n  with Parameters: {request.parameters}')
            cursor.execute(request.query, request.parameters)

            if not request.ro:
                if cursor.rowcount <= request.max_changing_rows or request.max_changing_rows == -1:
                    connection.commit()
                    request.add_result(cursor.rowcount)
                else:
                    connection.rollback()
                    raise ToManyRowsChanged(expected = request.max_changing_rows, received = cursor.rowcount)

            else:
                connection.rollback()
                rows = cursor.fetchall()
                request.add_result(rows)

    except Exception as err:
        raise err
    finally:
        if connection is not None:
            connection.close()


def sync_save_read(sql_statement: str, parameters: typing.Optional[Iterable] = None):
    r = SQLRequest(sql_statement, parameters, 0, True)
    save_access_sync([r])
    return r.result


def sync_save_write(sql_statement: str, parameters: typing.Optional[Iterable] = None, max_changing_rows=-1):
    r = SQLRequest(sql_statement, parameters, max_changing_rows, False)
    save_access_sync([r])
    return r.result
