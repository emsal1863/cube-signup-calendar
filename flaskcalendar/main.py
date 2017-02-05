from __future__ import print_function 
from flask import Flask
from flask import request, render_template, jsonify
import json
import datetime
import dateutil.parser
from werkzeug.datastructures import ImmutableDict

from db import db_connection


dbconn = db_connection.init()

app = Flask(__name__)


@app.route('/')
def calendar():
    return render_template("json.html")


@app.route('/data')
def return_data():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    # You'd normally use the variables above to limit the data returned
    # you don't want to return ALL events like in this code
    # but since no db or any real storage is implemented I'm just
    # returning data from a text file that contains json elements

    with open("flaskcalendar/events.json", "r") as input_data:
        # you should use something else here than just plaintext
        # check out jsonfiy method or the built in json module
        # http://flask.pocoo.org/docs/0.10/api/#module-flask.json
        return input_data.read()

@app.route('/calendar_event', methods=['GET', 'POST', 'PUT', 'DELETE'])
def calendar_event_rest():
    if request.method == 'GET':
        if 'id' not in request.args:
            d = {'error': 'need to pass in an id'}
            return jsonify(**d)
        else:
            with db_connection.DBContextManager(dbconn) as cxn:
                data = db_connection.read_time(cxn, request.args['id'])
                return jsonify(**data)

    elif request.method == 'POST':
        data = request.get_json()
        required_params = ['start_time', 'person']
        if any([i not in data for i in required_params]):
            return jsonify({'error': 'at least one required param missing'})

        start_time = dateutil.parser.parse(data['start_time'])
        try:
            end_time = dateutil.parser.parse(data['end_time'])
        except:
            end_time = None
        person = data['person']

        with db_connection.DBContextManager(dbconn) as cxn:
            ret_id = db_connection.insert_time(cxn, start_time, end_time, person)

            return jsonify({'id': ret_id[0]})

    elif request.method == 'PUT':
        data = request.get_json()
        required_params = ['id']
        if any([i not in data for i in required_params]):
            return jsonify({'error': 'at least one required param missing'})

        event_id = data['id']

        try:
            start_time = dateutil.parser.parse(data['start_time'])
        except:
            start_time = None

        try:
            end_time = dateutil.parser.parse(data['end_time'])
        except:
            end_time = None

        person = data.get('person')

        with db_connection.DBContextManager(dbconn) as cxn:
            ret = db_connection.edit_time(cxn, event_id, person, start_time, end_time)
            #print(ImmutableDict(ret))
            return jsonify(**ret)

        return json.dumps(data)

    elif request.method == 'DELETE':
        #print(request.args)
        #print('id' in request.args)
        data = request.args
        required_params = ('id',)
        if any([i not in request.args for i in required_params]):
            resp = jsonify({'error': 'at least one required param missing'})
            resp.status_code = 400
            return resp

        with db_connection.DBContextManager(dbconn) as cxn:
            db_connection.delete_time(cxn, int(request.args['id']))

        return ('', 204)

@app.route('/calendar_event_feed')
def calendar_event_multi_endpoint():
    # print(request.args)
    required_params = ('start', 'end')
    if any([i not in request.args for i in required_params]):
        return jsonify({'error': 'at least one required param missing'})
    else:
        global dbconn
        start_date = dateutil.parser.parse(request.args['start'])
        end_date = dateutil.parser.parse(request.args['end'])

        with db_connection.DBContextManager(dbconn) as cxn:
            data = db_connection.get_many(cxn, start_date, end_date)
            return json.dumps(data)

if __name__ == '__main__':
    app.debug = True
    dbconn = db_connection.init()
    print(dbconn)

    app.run()
