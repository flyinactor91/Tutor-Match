"""
Michael duPont
Controls connections to the database
"""

import os
import sqlite3
from flask import g
from TutorMatch import app

DB_PATH = os.path.dirname(os.path.abspath(__file__))+'/test.sqlite'

def make_dicts(curs: '', row):
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

def query(qstr: str, args: tuple=None, one: bool=False,
          return_type: str='Row') -> '[sqlite3.Row/dict]':
    """Query an SQLite database with or without args
    Setting 'one' to True will return a single item
    See get_db() for an explaination of return_type"""
    if args is None:
        args = tuple()
    curs = get_db(return_type=return_type).execute(qstr, args)
    rows = curs.fetchall()
    curs.close()
    return (rows[0] if rows else None) if one else rows

@app.teardown_appcontext
def close_connection(*_):
    """Close database connection if no longer in use"""
    dbconn = getattr(g, '_database', None)
    if dbconn is not None:
        dbconn.close()
