import mysql.connector
import os

import deadlines as dl


HOST = os.getenv("DB_HOST")
USER = os.getenv("DB_USER")
PASS = os.getenv("DB_PASS")
NAME = os.getenv("DB_NAME")

if not (HOST and USER and PASS and NAME):
    raise Exception("missing DB info")

db = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASS,
    database=NAME
)

cursor = db.cursor(prepared=True)


def query(query, params=()):
    cursor.execute(query, params)
    result = cursor.fetchall()
    db.commit()
    return result


def q_deadlines(query, params=()):
    cursor.execute(query, params)
    result = cursor.fetchall()
    db.commit()

    return [dl.Deadline(x) for x in result]
