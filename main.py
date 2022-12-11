import flask
from dbhandler import DBHandler

app = flask.Flask(__name__)

db = DBHandler('queue.db')

@app.route('/')
def index():
    #Static server for /index.html
    return flask.send_from_directory('static', 'templates/index.html')

#Creates a new queue
@app.route('/create', methods=['POST'])
def create():
    #Parameters: title, description, display_current
    # If a parameter is missing, return 400
    if 'title' not in flask.request.form or 'description' not in flask.request.form or 'display_current' not in flask.request.form:
        return flask.Response(status=400)
    id = db.create_queue(flask.request.form['title'], flask.request.form['description'], flask.request.form['display_current'])
    # Set the cookie for the queue
    res = flask.make_response(flask.redirect('/admin'))
    res.set_cookie('queue_id', str(id))
    return res


@app.route('/public/info')
def get_info():
    id = None
    try:
        id = flask.request.cookies.get('queue_id')
    except:
        # Throw a 400 if the cookie is missing
        return flask.Response(status=400)
    # Returns a json object with the title, description and display_current and the code
    queue = db.get_queue(id)
    if queue is None:
        return flask.Response(status=404)
    return flask.jsonify({'title': queue[1], 'description': queue[2], 'display_current': queue[3], 'code': queue[4]})

@app.route('/public/getnext')
def get_next():
    id = flask.request.cookies.get('queue_id')
    # Returns the ID of the next entry
    entry = db.get_next_queue_entry(id)
    if entry is None:
        return flask.Response(status=404)
    return flask.jsonify({'id': entry[0]})

# domain.com/code redirects the user to /<id>/public
@app.route('/join/<code>')
def join_usr(code):
    # Returns the ID of the next entry
    queue = db.get_queue(code)
    if queue is None:
        return flask.Response(status=404)
    res = flask.make_response(flask.redirect('/public/queue'))
    res.set_cookie('queue_id', str(queue[0]))
    res.set_cookie('user', 'public')
    return res

@app.route('/join/TA/<code>')
def join_TA(code):
    # Returns the ID of the next entry
    queue = db.get_queue(code)
    if queue is None:
        return flask.Response(status=404)
    res = flask.make_response(flask.redirect('/private/TA'))
    res.set_cookie('queue_id', str(queue[0]))
    res.set_cookie('user', 'public')
    return res


@app.route('/public/queue')
def public():
    #Static server for public.html
    return flask.send_from_directory('static', 'templates/queue.html')

@app.route('/public/addentry', methods=['POST'])
def add_entry():
    id = flask.request.cookies.get('queue_id')
    #Parameters: name, question, extra
    # If a parameter is missing, return 400
    if 'name' not in flask.request.form:
        return flask.Response(status=400)
    entry_id = db.add_queue_entry(id, flask.request.form['name'], flask.request.form['question'], flask.request.form['extra'])
    return flask.jsonify({'id': entry_id})

@app.route('/public/board')
def public_board():
    return flask.send_from_directory('static', 'templates/board.html')


@app.route('/private/getqueue')
def get_queue():
    # Returns all the entries in the queue with status "status"
    # Parameters: status
    # If a parameter is missing, return 400

    id = flask.request.cookies.get('queue_id')
    entries = db.get_queue_entries(id)
    # [ID , Queue ID , Name , Question , Extra , Timestamp , Status (0 = waiting, 1 = being answered, 2 = answered) , Handler Name]

    return flask.jsonify({'entries': entries})

@app.route('/private/updatestatus', methods=['POST'])
def update_status():
    # Parameters: id, new status
    # If a parameter is missing, return 400
    if 'entryId' not in flask.request.form or 'newStatus' not in flask.request.form:
        return flask.Response(status=400)
    db.change_queue_entry_status(flask.request.form['entryId'], flask.request.form['newStatus'], "somebody")
    return flask.Response(status=200)

@app.route('/private/admin')
def admin_board():
    return flask.send_from_directory('static', 'templates/admin.html')

@app.route('/private/TA')
def admin_TA():
    return flask.send_from_directory('static', 'templates/TA.html')

@app.route('/private/TA/getnext')
def get_next_TA():
    id = flask.request.cookies.get('queue_id')
    # Returns the ID of the next entry
    entry = db.get_next_queue_entry(id)
    if entry is None:
        return flask.Response(status=404)
    return flask.jsonify({'entry': entry})

@app.route('/private/TA/updatestatus', methods=['POST'])
def update_status_TA():
    # Parameters: id, new status
    # If a parameter is missing, return 400
    if 'entryId' not in flask.request.form or 'newStatus' not in flask.request.form:
        return flask.Response(status=400)
    db.change_queue_entry_status(flask.request.form['entryId'], flask.request.form['newStatus'], "somebody")
    return flask.Response(status=200)
   
if __name__ == '__main__':
    app.run()
