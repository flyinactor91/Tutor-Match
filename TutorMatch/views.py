"""
Michael duPont
Primary routing controller
"""

import functools
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
        ret = func(*args, **kwargs)
        if not raw:
            ret = jsonify(ret)
        return ret
    return wrapper

##--- Helper Functions ---##

def users_base(ext: str='', args: tuple=None) -> [dict]:
    """Returns basic User data plus an optional given 'WHERE' clause"""
    query = ("SELECT u.id, u.name, ut.name AS 'type' "
             "FROM User u INNER JOIN User_Type ut ON u.utype=ut.id ")
    query += ext
    return db.query(query, args, return_type='dict')

def skills_for_user(user_id: int) -> [str]:
    """Returns a list of skills names for a given user_id"""
    query = ("SELECT s.name FROM Skill s "
             "INNER JOIN User_Skill u_s ON s.id=u_s.skill_id "
             "WHERE u_s.user_id=?")
    return [r[0] for r in db.query(query, (user_id,))]

def get_skills_for_user_dict(udict: dict, remove_id: bool=True):
    """Adds skills to a list of user dicts"""
    for i, user in enumerate(udict):
        udict[i]['skills'] = list(skills_for_user(user['id']))
        if remove_id:
            del udict[i]['id']
    return udict

##--- Routing ---##

@app.route('/')
def home() -> str:
    return "Hello"

# Users

@app.route('/users')
@output_str
def users() -> [dict]:
    """Returns details on all users"""
    return get_skills_for_user_dict(users_base())

@app.route('/users/count')
@output_str
def user_count() -> int:
    """Returns the total number of users"""
    return db.query('SELECT count(id) FROM User', one=True)[0]

@app.route('/users/<string:utype>')
@output_str
def users_by_type(utype: str) -> [dict]:
    """Returns details on users matching a given type"""
    query_ext = ' WHERE utype IN (SELECT id FROM User_Type WHERE name=?)'
    return get_skills_for_user_dict(users_base(query_ext, (utype,)))

@app.route('/users/<string:utype>/count')
@output_str
def user_count_by_type(utype: str) -> int:
    """Returns the total number of users that match a given type"""
    query = ("SELECT count(id) FROM User WHERE utype IN "
             "(SELECT id FROM User_Type WHERE name=?)")
    return db.query(query, (utype.lower(),), one=True)[0]

@app.route('/users/with/<string:skill>/count')
@output_str
def user_count_by_skill(skill: str) -> int:
    """Returns the total number of users with a given skill"""
    query = ("SELECT count(u.id) FROM User u, Skill s, User_Skill u_s "
             "WHERE u.id=u_s.user_id AND u_s.skill_id=s.id AND s.name=?")
    return db.query(query, (skill.lower(),), one=True)[0]

@app.route('/users/<string:utype>/with/<string:skill>/count')
@output_str
def user_count_by_type_and_skill(utype: str, skill: str) -> int:
    """Returns the total number of users that match both a given type and skill"""
    query = ("SELECT count(u.id) FROM User u, Skill s, User_Skill u_s "
             "WHERE u.id=u_s.user_id AND u_s.skill_id=s.id AND s.name=? "
             "AND u.utype IN (SELECT id FROM User_Type WHERE name=?)")
    return db.query(query, (skill.lower(), utype.lower(),), one=True)[0]

# Skills

@app.route('/skills')
@output_str
def skills() -> [dict]:
    """Returns a list of dicts containing all skill details"""
    return db.query("SELECT name, display_name FROM Skill", return_type='dict')

@app.route('/skills/count')
@output_str
def skill_count() -> int:
    """Returns the total number of skills"""
    query = "SELECT count(id) FROM Skill"
    return db.query(query, one=True)[0]
