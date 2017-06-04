import os
import json
from functools import wraps

from flask import redirect, request, render_template, flash
from flask import Flask, url_for, session as login_session
from flask import jsonify, make_response, send_from_directory


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, template_folder='../templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


G_SOURCE = 'client_secrets.json'
LI_SOURCE = 'ln_client_secrets.json'

G_CID = json.loads(open(G_SOURCE, 'r').read())['web']['client_id']
LI_ID = json.loads(open(LI_SOURCE, 'r').read())['web']['app_id']
LI_SECRET = json.loads(open(LI_SOURCE, 'r').read())['web']['app_secret']
LI_RET_URI = json.loads(open(LI_SOURCE, 'r').read())['web']['return_uri']
LI_SCOPE = "r_basicprofile r_emailaddress"


def login_required(func):
    @wraps(func) # this requires an import
    def wrapper():
        if 'name' not in login_session:
            return redirect(url_for('showLogin'))
        else:
            func()
    return wrapper

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def storeTokenInfo(token):
    global token_info
    token_info = token

def setCredentials(new_credential):
    global credentials
    credentials = new_credential


def getUserID(email):
  try:
    user = session.query(User).filter_by(email = email).one()
    return user.id
  except:
    return None

def getUserInfo(user_id):
        user = session.query(User).filter_by(id=user_id).one()
        return user

def getUser(email):
  try:
    user = session.query(User).filter_by(email = email).one()
    return user
  except:
    return None

def createSession():
  if login_session.get('state') is None:
    login_session['state'] = ''.join(
      random.choice(string.ascii_uppercase + string.digits)for x in xrange(32))


def responseHelper(message, response_code):
  response = make_response(json.dumps(message), response_code)
  response.headers['Content-Type'] = 'application/json'
  print response
  return response