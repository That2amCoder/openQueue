import flask
from dbhandler import DBHandler
import qrcode
import yaml, json
import io, os
import base64
app = flask.Flask(__name__)

db = DBHandler('db/queue.db')
domain = "127.0.0.0"
port = 5000

@app.route('/')
def index():
    #Static server for /index.html
    return flask.send_from_directory('static', 'templates/index.html')

#Creates a new queue
@app.route('/create', methods=['POST'])
def create():
    #Parameters: title, description, display_current
    # If a parameter is missing, return 400
    display_current = False
    if 'title' not in flask.request.form or 'description' not in flask.request.form:
        return flask.Response(status=400)
    id, authcode, code = db.create_queue(flask.request.form['title'], flask.request.form['description'], display_current)
    print(flask.request.form)
    # if "form" in the post request, then the user is creating a form
    if 'questionList' in flask.request.form:
        # Format of the form is JSON { "forms": [ { "name": "Name", "type": "text" }, { "name": "Age", "type": "number" }]
        # Load the json
        form = json.loads(flask.request.form['questionList'])
        x = 0
        for field in form['forms']:
            db.add_queue_form(id, field['text'],field['subtext'], field['type'], field['options'], field['required'], field['order'])
            x += 1
    else: # if there is no form, then create a default form
        db.add_queue_form(id, 'Name', 'text',0, '', True, 0)
        db.add_queue_form(id, 'Age', 'number',0, '', True, 1)

    res = flask.make_response(flask.redirect('/private/admin'))
    res.set_cookie('authcode', authcode)
    # Set the cookie for the queue
    res.set_cookie('queue_id', str(id))
    
    # Create a qr code for the queue in the form of a png, and have the link be the domain.com/join/<code>
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(domain + ':' + str(port) + '/join/' + code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save('static/qr/' + str(id) + '.png')
 
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

    # load the qr code image
    qr = None
    with open('static/qr/' + str(id) + '.png', 'rb') as f:
        qr = base64.b64encode(f.read()).decode('utf-8')

    queue_json = {'title': queue[1], 'description': queue[2], 'display_current': queue[3], 'code': queue[4], 'current': queue[7], 'qr': qr }

    # Get the forms for the queue
    forms = db.get_queue_forms(id)
    queue_json['forms'] = []
    for form in forms:
        queue_json['forms'].append({'id': form[0], 'text': form[2], 'subtext': form[3], 'type': form[4], 'options': form[5], 'required': form[6], 'order': form[7]})
    
    #if there is an authcode, return it
    if 'authcode' in flask.request.cookies:
        auth_code = flask.request.cookies.get('authcode')
        if db.verify_auth_code(id, auth_code):
            queue_json['authcode'] = flask.request.cookies.get('authcode')
    

    return flask.jsonify(queue_json)

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

@app.route('/handler/setname', methods=['POST'])
def set_name():
    #Parameters: name
    # If a parameter is missing, return 400
    if 'name' not in flask.request.form:
        return flask.Response(status=400)
    res = flask.make_response(flask.redirect('/private/handler'))
    res.set_cookie('handler-name', flask.request.form['name'])
    return res

@app.route('/join/handler/<code>')
def join_handler(code):
    # Returns the ID of the next entry
    queue = db.get_auth_queue(code)
    if queue is None:
        return flask.Response(status=404)

    res = None
    # If there is no "handler-name" cookie, redirect to /<id>/handlerjoin
    if 'handler-name' not in flask.request.cookies:
        res = flask.make_response(flask.send_file('static/templates/handlerjoin.html'))
    else:        
        res = flask.make_response(flask.redirect('/private/handler'))
    res.set_cookie('authcode', code)
    # Else, redirect to /private/handler
    #Get username from 
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
    if 'data' not in flask.request.form:
        return flask.Response(status=400)
    entry_id = db.add_queue_entry(id, flask.request.form['data'])
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
    auth_code = flask.request.cookies.get('authcode')
    if db.verify_auth_code(id, auth_code) == None:
        return flask.Response(status=401)

    entries = db.get_queue_entries(id)
    # [ID , Queue ID , Name , Question , Extra , Timestamp , Status (0 = waiting, 1 = being answered, 2 = answered) , Handler Name]

    return flask.jsonify({'entries': entries})

@app.route('/private/updatestatus', methods=['POST'])
def update_status():
    # Parameters: id, new status
    # If a parameter is missing, return 400

    id = flask.request.cookies.get('queue_id')
    auth_code = flask.request.cookies.get('authcode')
    if db.verify_auth_code(id, auth_code) == None:
        return flask.Response(status=401)

    if 'entryId' not in flask.request.form or 'newStatus' not in flask.request.form:
        return flask.Response(status=400)
    handlername = flask.request.cookies.get('handler-name')
    db.change_queue_entry_status(flask.request.form['entryId'], flask.request.form['newStatus'], handlername)
    return flask.Response(status=200)

@app.route('/private/admin')
def admin_board():
    id = flask.request.cookies.get('queue_id')
    auth_code = flask.request.cookies.get('authcode')
    if db.verify_auth_code(id, auth_code) == None:
        return flask.Response(status=401)
    return flask.send_from_directory('static', 'templates/admin.html')

@app.route('/private/handler')
def admin_handler():
    id = flask.request.cookies.get('queue_id')
    auth_code = flask.request.cookies.get('authcode')
    if db.verify_auth_code(id, auth_code) == None:
        return flask.Response(status=401)
    return flask.send_from_directory('static', 'templates/handler-terminal.html')

@app.route('/private/handler/getnext')
def get_next_handler():

    id = flask.request.cookies.get('queue_id')
    auth_code = flask.request.cookies.get('authcode')
    if db.verify_auth_code(id, auth_code) == None:
        return flask.Response(status=401)

    # Returns the ID of the next entry
    entry = db.get_next_queue_entry(id)
    return flask.jsonify({'entry': entry})

@app.route('/private/handler/updatestatus', methods=['POST'])
def update_status_handler():

    id = flask.request.cookies.get('queue_id')
    auth_code = flask.request.cookies.get('authcode')
    if db.verify_auth_code(id, auth_code) == None:
        return flask.Response(status=401)

    # Parameters: id, new status
    # If a parameter is missing, return 400
    if 'entryId' not in flask.request.form or 'newStatus' not in flask.request.form:
        return flask.Response(status=400)
    handler = flask.request.cookies.get('handler-name')
    db.change_queue_entry_status(flask.request.form['entryId'], flask.request.form['newStatus'], handler)
    return flask.Response(status=200)
   
# Any request that is /static/<path> will be served from the static folder
@app.route('/static/<path:path>')
def send_static(path):
    if ".." in path:
        return flask.Response(status=400)
    return flask.send_from_directory('static', path)

if __name__ == '__main__':
    # If the "db" folder doesn't exist, create it
    if not os.path.exists('db'):
        os.makedirs('db')
    
    # If static/qr doesn't exist, create it
    if not os.path.exists('static/qr'):
        os.makedirs('static/qr')
    

    # Open conf.yaml
    config = None
    with open('conf.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
        # Read the domain and port from the config file
        domain = config['host']
        port = config['port']
        debug = config['debug']


    app.run(host=domain, port=port, debug=debug)
