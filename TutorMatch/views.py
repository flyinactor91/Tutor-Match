import sqlite3
from flask import g, request, Response
from TutorMatch import app

##--- Database Operations ---##

DB_PATH = 'test.sqlite'

def get_db() -> sqlite3.Connection:
    dbconn = getattr(g, '_database', None)
    if dbconn is None:
        dbconn = g._database = sqlite3.connect(DB_PATH)
    dbconn.row_factory = sqlite3.Row
    return dbconn

def query_db(query: str, args: tuple=None, one: bool=False) -> [sqlite3.Row]:
    if args is None:
        args = tuple()
    curs = get_db().execute(query, args)
    rows = curs.fetchall()
    curs.close()
    return (rows[0] if rows else None) if one else rows

@app.teardown_appcontext
def close_connection(excp: Exception):
    dbconn = getattr(g, '_database', None)
    if dbconn is not None:
        dbconn.close()

##--- Routing ---##

@app.route('/')
def home() -> str:
    return "Hello"

@app.route('/users/count')
def get_user_total():
    return str(query_db('SELECT count(id) FROM User', one=True)[0])

@app.route('/users/<string:utype>/count')
def get_user_count(utype: str) -> str:
    query = ("SELECT count(id) FROM User WHERE utype IN "
             "(SELECT id FROM User_Type WHERE name=?)")
    return str(query_db(query, (utype.lower(),), one=True)[0])
