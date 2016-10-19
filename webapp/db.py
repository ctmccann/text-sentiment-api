'''
This module abstracts the specifics of the current DBMS away from the rest of
the app so that we can switch to a more hefty, distributed DB at some point in
the future.

For now we will just use SQLite so that we can get things up-and-running quickly.
'''

import sqlite3


DB_FILE_NAME = 'queries_v1.db'


def d():
    '''Use this function to get a cursor to help you debug things quickly
    using the python shell.'''
    conn = sqlite3.connect(DB_FILE_NAME)
    c = conn.cursor()
    return c


def dump_table(table_name):
    conn = sqlite3.connect(DB_FILE_NAME)
    c = conn.cursor()
    if table_name in ['queries']:
        return list(c.execute('''
            SELECT * FROM {};
            '''.format(table_name)))


def init():
    conn = sqlite3.connect(DB_FILE_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            query_id INTEGER PRIMARY KEY ASC,
            timestamp TEXT,                     -- time when inserted
            parameters TEXT,                    -- JSON paramerters of this query
            response TEXT,                      -- JSON response (query's answer)
            process_time REAL                   -- processing time in milliseconds
        );
        ''')

    c.execute('''
        CREATE INDEX IF NOT EXISTS queries_timestamp
        ON queries(timestamp);
        ''')

    conn.commit()


def insert_query(parameters_json, response_json, process_time_ms):
    conn = sqlite3.connect(DB_FILE_NAME)
    c = conn.cursor()

    c.execute('''
        INSERT INTO queries
        (timestamp, parameters, response, process_time)
        VALUES
        (strftime('%Y-%m-%d %H:%M:%f'), ?, ?, ?);
        ''', (parameters_json, response_json, process_time_ms))
    query_id = c.lastrowid

    conn.commit()

    return query_id


def get_avg_process_time(request_interval):
    conn = sqlite3.connect(DB_FILE_NAME)
    c = conn.cursor()
    res = list(c.execute('''
        SELECT AVG(process_time)
        FROM queries
        ORDER BY query_id DESC
        LIMIT 4'''))                # TODO fix this
    val = res[0][0]
    if val is None:
        val = 0.0
    return val


def get_num_requests(time_interval_seconds):
    conn = sqlite3.connect(DB_FILE_NAME)
    c = conn.cursor()
    time_offset_str = "-{:.4f} second".format(float(time_interval_seconds))
    res = list(c.execute('''
        SELECT COUNT(*)
        FROM queries
        WHERE timestamp >= strftime('%Y-%m-%d %H:%M:%f', 'now', ?);''',
        (time_offset_str, )))
    return res[0][0]

