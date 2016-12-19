from __future__ import print_function
from flask import Flask
from flask import request, render_template, jsonify
import json


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

@app.route('/calendar_event')
def calendar_event_rest():
    if request.method == 'GET':
        if 'id' not in request.args:
            d = {'error': 'need to pass in an id'}
            return jsonify(**d)
        else:
            print(request.args)
            return jsonify(**{'id': request.args['id']})

    elif request.method == 'POST':
        pass
    elif request.method == 'PUT':
        pass
    elif request.method == 'DELETE':
        pass
    return 'ayy lmoa'


if __name__ == '__main__':
    app.debug = True
    app.run()
