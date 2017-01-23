"""
Michael duPont
Primary routing controller
"""

import functools
import sqlite3
from flask import g, jsonify#, request, Response
from TutorMatch import app

##--- Database Operations ---##

DB_PATH = 'test.sqlite'

def make_dicts(curs, row):
    """Converts an SQLite row into a dict"""
    return dict((curs.description[idx][0], value) for idx, value in enumerate(row))

def get_db(return_type: str='Row') -> sqlite3.Connection:
    """Returns a new or existing SQLite database connection
    return_type can be 'Row' for sqlite3.Row or 'dict' for dict"""
    dbconn = getattr(g, '_database', None)
    if dbconn is None:
        dbconn = g._database = sqlite3.connect(DB_PATH)
    if return_type == 'Row':
        dbconn.row_factory = sqlite3.Row
    elif return_type == 'dict':
        dbconn.row_factory = make_dicts
    else:
        raise ValueError('Not a valid return type')
    return dbconn

def query_db(query: str, args: tuple=None, one: bool=False,
             return_type: str='Row') -> '[sqlite3.Row/dict]':
    """Query an SQLite database with or without args
    Setting 'one' to True will return a single item
    See get_db() for an explaination of return_type"""
    if args is None:
        args = tuple()
    curs = get_db(return_type=return_type).execute(query, args)
    rows = curs.fetchall()
    curs.close()
    return (rows[0] if rows else None) if one else rows

@app.teardown_appcontext
def close_connection(*_):
    """Close database connection if no longer in use"""
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
            ret = jsonify(ret)
        return ret
    return wrapper

##--- Helper Functions ---##

def users_base() -> [dict]:
    """Returns basic User data"""
    query = ("SELECT u.id, u.name, ut.name AS 'type' "
             "FROM User u INNER JOIN User_Type ut ON u.utype=ut.id")
    return query_db(query, return_type='dict')

def skills_for_user(user_id: int) -> [str]:
    """Returns a list of skills names for a given user_id"""
    query = ("SELECT s.name FROM Skill s "
             "INNER JOIN User_Skill u_s ON s.id=u_s.skill_id "
             "WHERE u_s.user_id=?")
    return [r[0] for r in query_db(query, (user_id,))]

##--- Routing ---##

@app.route('/')
def home() -> str:
    return "Hello"

# Users

@app.route('/users')
@output_str
def users() -> [dict]:
    """Returns details on all users"""
    ret = users_base()
    for i, user in enumerate(ret):
        ret[i]['skills'] = list(skills_for_user(user['id']))
        del ret[i]['id']
    return ret

@app.route('/users/count')
@output_str
def user_count() -> int:
    """Returns the total number of users"""
    return query_db('SELECT count(id) FROM User', one=True)[0]

@app.route('/users/<string:utype>/count')
@output_str
def user_count_by_type(utype: str) -> int:
    """Returns the total number of users that match a given type"""
    query = ("SELECT count(id) FROM User WHERE utype IN "
             "(SELECT id FROM User_Type WHERE name=?)")
    return query_db(query, (utype.lower(),), one=True)[0]

@app.route('/users/with/<string:skill>/count')
@output_str
def user_count_by_skill(skill: str) -> int:
    """Returns the total number of users with a given skill"""
    query = ("SELECT count(u.id) FROM User u, Skill s, User_Skill u_s "
             "WHERE u.id=u_s.user_id AND u_s.skill_id=s.id AND s.name=?")
    return query_db(query, (skill.lower(),), one=True)[0]

@app.route('/users/<string:utype>/with/<string:skill>/count')
@output_str
def user_count_by_type_and_skill(utype: str, skill: str) -> int:
    """Returns the total number of users that match both a given type and skill"""
    query = ("SELECT count(u.id) FROM User u, Skill s, User_Skill u_s "
             "WHERE u.id=u_s.user_id AND u_s.skill_id=s.id AND s.name=? "
             "AND u.utype IN (SELECT id FROM User_Type WHERE name=?)")
    return query_db(query, (skill.lower(), utype.lower(),), one=True)[0]

# Skills

@app.route('/skills')
@output_str
def skills() -> [dict]:
    """Returns a list of dicts containing all skill details"""
    return query_db("SELECT name, display_name FROM Skill", return_type='dict')

@app.route('/skills/count')
@output_str
def skill_count() -> int:
    """Returns the total number of skills"""
    query = "SELECT count(id) FROM Skill"
    return query_db(query, one=True)[0]
