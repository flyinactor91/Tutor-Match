#!/usr/bin/python3

"""
Michael duPont
"""

import logging
import sqlite3
from json import load

conn = sqlite3.connect('../TutorMatch/test.sqlite')
curs = conn.cursor()
dbdata = load(open('test_data.json'))

for key, settings in dbdata.items():
    cols = settings['columns']
    query = "CREATE TABLE {} (id,{})".format(key, ','.join(cols))
    logging.debug('Table query: %s', query)
    curs.execute(query)
    rows = [[i, *vals] for i, vals in enumerate(settings['rows'])]
    logging.debug('Prepended rows: %s', rows)
    query = "INSERT INTO {} VALUES ({})".format(key, ','.join(['?']*len(rows[0])))
    logging.debug('Insert query: %s', query)
    curs.executemany(query, rows)
    conn.commit()

conn.close()
