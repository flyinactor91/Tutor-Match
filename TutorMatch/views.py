"""
Michael duPont
Primary routing controller
"""

import functools
import os
from json import load
from flask import jsonify
from TutorMatch import app
import TutorMatch.dbconn as db

##--- Custom Decorators ---##

def output_str(func):
    """This decorator adds the 'raw' boolean keyword to functions.
    When applied, the function's output will be converted to a string
    unless the function call includes raw=True
    """
    #This decorator allows us to use our custom decs alongside Flask's routing decs
    @functools.wraps(func)
    def wrapper(*args, raw: bool=False, **kwargs):
        """jsonify the output of a function if not 'raw'"""
        ret = func(*args, **kwargs)
        if not raw:
            ret = jsonify(ret)
        return ret
    return wrapper

##--- Query Vars ---##

QUERIES = load(open(os.path.dirname(os.path.abspath(__file__))+'/queries.json'))

USER_COLS = 'u.id, u.name, u.utype AS "type"'
SKILL_COLS = 'name, display_name'
COUNT = 'count(*)'

##--- Helper Functions ---##

def skills_for_user(user_id: int) -> [str]:
    """Returns a list of skills names for a given user_id"""
    query = QUERIES['skills']['for-user'].format('s.name')
    return [r[0] for r in db.query(query, (user_id,))]

def get_skills_for_user_dict(udict: dict, remove_id: bool=True):
    """Adds skills to a list of user dicts"""
    for i, user in enumerate(udict):
        udict[i]['skills'] = list(skills_for_user(user['id']))
        if remove_id:
            del udict[i]['id']
    return udict

def get_users(subquery: str, args: tuple=None) -> [dict]:
    """Returns a full list of users utilizing a given subquery key and value args"""
    query = QUERIES['users'][subquery].format(USER_COLS)
    base = db.query(query, args, return_type='dict')
    return get_skills_for_user_dict(base)

def get_count(table: str, subquery: str, args: tuple=None) -> int:
    """Returns the number of elements in a given table matching a given subquery key"""
    query = QUERIES[table][subquery].format(COUNT)
    return db.query(query, args, one=True)[0]

##--- Routing ---##

@app.route('/')
def home() -> str:
    return "Hello"

# Users

@app.route('/users')
@output_str
def users() -> [dict]:
    """Returns details on all users"""
    return get_users('base')

@app.route('/users/count')
@output_str
def user_count() -> int:
    """Returns the total number of users"""
    return get_count('users', 'base')

@app.route('/users/<string:utype>')
@output_str
def users_by_type(utype: str) -> [dict]:
    """Returns details on users matching a given type"""
    return get_users('type', (utype.lower(),))

@app.route('/users/<string:utype>/count')
@output_str
def user_count_by_type(utype: str) -> int:
    """Returns the total number of users that match a given type"""
    return get_count('users', 'type', (utype.lower(),))

@app.route('/users/with/<string:skill>')
@output_str
def users_by_skill(skill: str) -> [dict]:
    """Returns details on users matching a given skill"""
    return get_users('skill', (skill.lower(),))

@app.route('/users/with/<string:skill>/count')
@output_str
def user_count_by_skill(skill: str) -> int:
    """Returns the total number of users with a given skill"""
    return get_count('users', 'skill', (skill.lower(),))

@app.route('/users/<string:utype>/with/<string:skill>')
@output_str
def users_by_type_and_skill(utype: str, skill: str):
    """Returns details on user that match both a given type and skill"""
    return get_users('type-skill', (utype.lower(), skill.lower(),))

@app.route('/users/<string:utype>/with/<string:skill>/count')
@output_str
def user_count_by_type_and_skill(utype: str, skill: str) -> int:
    """Returns the total number of users that match both a given type and skill"""
    return get_count('users', 'type-skill', (utype.lower(), skill.lower(),))

# Skills

@app.route('/skills')
@output_str
def skills() -> [dict]:
    """Returns a list of dicts containing all skill details"""
    query = QUERIES['skills']['base'].format(SKILL_COLS)
    return db.query(query, return_type='dict')

@app.route('/skills/count')
@output_str
def skill_count() -> int:
    """Returns the total number of skills"""
    return get_count('skills', 'base')
