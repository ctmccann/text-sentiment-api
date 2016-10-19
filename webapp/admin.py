VERSION_STR = 'admin'


import db
import time
from app import APP_NAME
from error import Error
from flask import Blueprint, jsonify, request, g

blueprint = Blueprint(VERSION_STR, __name__)


LOAD_TIME = time.time()


def avg_response_time():
    return db.get_avg_process_time(g.request_interval)


def num_requests():
    return db.get_num_requests(g.time_interval)


def uptime():
    return time.time() - LOAD_TIME


INFO = {'avg_response_time': avg_response_time,
        'num_requests': num_requests,
        'service_name': lambda: APP_NAME,
        'uptime': uptime
       }


@blueprint.route('/status')
def status():
    '''
    Get current status
    This endpoint provides a remote way to monitor this service
    and get status information about how well it is running.
    ---
    tags:
      - admin

    responses:
      200:
        description: A status info object
        schema:
          $ref: '#/definitions/StatusInfo'
      default:
        description: Unexpected error
        schema:
          $ref: '#/definitions/Error'

    parameters:
      - name: include_keys
        in: query
        description: A array of the keys that should be included in the response (default is all keys)
        required: false
        type: array
      - name: exclude_keys
        in: query
        description: A array of keys that should be excluded from the response (default is no keys)
        required: false
        type: array
      - name: request_interval
        in: query
        description: The number of recent requests to include when calculating 'avg_response_time' (default=100)
        required: false
        type: integer
      - name: time_interval
        in: query
        description: The number of seconds of recent activity to include when calculating 'num_requests' (default=60)
        required: false
        type: integer

    definitions:
      - schema:
          id: StatusInfo
          type: object
          required:
            - service_name
          properties:
            uptime:
              type: integer
              description: the number of seconds this service has been running
            num_requests:
              type: integer
              description: the number of requests this service has received in the last 'time_interval' number of seconds
            avg_response_time:
              type: number
              description: the average time in milliseconds that it took to generate the last 'request_interval' responses
            service_name:
              type: string
              description: the name of this service
      - schema:
          id: Error
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: integer
              description: Basic opaque status code
            message:
              type: string
              description: the human readable description of this error's error code
    '''
    include_keys = request.args.get('include_keys', ','.join(INFO.keys())).split(',')
    exclude_keys = request.args.get('exclude_keys', '').split(',')
    g.request_interval = request.args.get('request_interval', 100)
    g.time_interval = request.args.get('time_interval', 60)
    keys = (set(INFO.keys()) & set(include_keys)) - set(exclude_keys)
    res = {k: INFO[k]() for k in keys}
    return jsonify(res)


@blueprint.route('/table')
def table():
    '''
    Dump a table
    This is a debugging endpoint used to dump the contents of a table as JSON.
    ---
    tags:
      - admin

    responses:
      200:
        description: A list of rows in the table
      default:
        description: Unexpected error
        schema:
          $ref: '#/definitions/Error'

    parameters:
      - name: table_name
        in: query
        description: The name of the table to dump
        required: true
        type: string
    '''
    table_name = request.args.get('table_name', '')
    d = {'contents': db.dump_table(table_name)}
    return jsonify(d)


from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
