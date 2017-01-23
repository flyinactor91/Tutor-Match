import functools
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

##--- Custom Decorators ---##

def output_str(func):
    """This decorator adds the 'raw' boolean keyword to functions.
    When applied, the function's output will be converted to a string
    unless the function call includes raw=True
    """
    #This decorator allows us to use our custom decs alongside Flask's routing decs
    @functools.wraps(func)
    def wrapper(*args, raw: bool=False, **kwargs):
        ret = func(*args, **kwargs)
        if not raw:
            ret = str(ret)
        return ret
    return wrapper

##--- Routing ---##

@app.route('/')
def home() -> str:
    return "Hello"

@app.route('/users/count')
@output_str
def user_total() -> int:
    return query_db('SELECT count(id) FROM User', one=True)[0]

@app.route('/users/<string:utype>/count')
@output_str
def user_count_by_type(utype: str) -> int:
    query = ("SELECT count(id) FROM User WHERE utype IN "
             "(SELECT id FROM User_Type WHERE name=?)")
    return query_db(query, (utype.lower(),), one=True)[0]

@app.route('/users/with/<string:skill>/count')
@output_str
def user_count_by_skill(skill: str) -> int:
    query = ("SELECT count(u.id) FROM User u, Skill s, User_Skill u_s "
             "WHERE u.id=u_s.user_id AND u_s.skill_id=s.id AND s.name=?")
    return query_db(query, (skill.lower(),), one=True)[0]

@app.route('/users/<string:utype>/with/<string:skill>/count')
@output_str
def user_count_by_type_and_skill(utype: str, skill: str) -> int:
    query = ("SELECT count(u.id) FROM User u, Skill s, User_Skill u_s "
             "WHERE u.id=u_s.user_id AND u_s.skill_id=s.id AND s.name=? "
             "AND u.utype IN (SELECT id FROM User_Type WHERE name=?)")
    return query_db(query, (skill.lower(), utype.lower(),), one=True)[0]
