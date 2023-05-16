import psycopg2
import os

import deadlines as dl


HOST = os.getenv("DB_HOST")
USER = os.getenv("DB_USER")
PASS = os.getenv("DB_PASS")
NAME = os.getenv("DB_NAME")

if not (HOST and USER and PASS and NAME):
    raise Exception("missing DB info")


def query(query, params=()):
    with psycopg2.connect(
        host=HOST,
        user=USER,
        password=PASS,
        database=NAME
    ) as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        connection.commit()
        return result


def q_deadlines(query, params=()):
    with psycopg2.connect(
        host=HOST,
        user=USER,
        password=PASS,
        database=NAME
    ) as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        connection.commit()

        return [dl.Deadline(x) for x in result]
