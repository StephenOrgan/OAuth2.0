import httplib2
import requests
import json
from itemcatalog_db_helper import *
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from handlers.utility_methods import checkAuthorizedState, responseHelper, setCredentials, storeTokenInfo
from flask import Flask, flash, make_response, Blueprint, request, url_for, session as login_session

google_sign_in = Blueprint("google_login", __name__, template_folder="../templates")
G_SOURCE = 'client_secrets.json'
G_CID = json.loads(open(G_SOURCE, 'r').read())['web']['client_id']

db = DBHelper()

def storeTokenInfo(token):
    global token_info
    token_info = token

def setCredentials(new_credential):
    global credentials
    credentials = new_credential

@google_sign_in.route('/gconnect', methods=['POST'])
def gconnect():
  return checkIfGoogleAuthorized(request)

def checkAuthorizedState(client_state):
  return client_state == login_session['state']

def checkIfGoogleAuthorized(client_request):
  if not checkAuthorizedState(client_request.args.get('state')):
      return responseHelper('Invalid authentication paramaters.', 401)
  else:
      request_data = client_request.data
      return tryOAuthFlow(request_data)

def tryOAuthFlow(request_data):
  try:
    oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'
    setCredentials(oauth_flow.step2_exchange(request_data))
    return validateToken()
  except FlowExchangeError:
    return responseHelper('Failed to upgrade the authorization code.', 401)

def validateToken():
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % credentials.access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  if result.get('error') is not None:
    return responseHelper(result.get('error'), 500)
  else:
    storeTokenInfo(result)
    return checkTokenAndCredentials()


def checkTokenAndCredentials():
  if token_info['user_id'] != credentials.id_token['sub']:
    return responseHelper('Token\'s user ID doesn\'t match given user ID.', 401)
  else:
    return checkIfTokenIssuedToClient()

def checkIfTokenIssuedToClient():
        if token_info['issued_to'] != G_CID:
            return responseHelper('Token\'s client ID does not match.', 401)
        else:
            return checkIfUserLoggedIn()


def checkIfUserLoggedIn():
    if login_session.get('credentials') is not None:
        if credentials.id_token['sub'] == login_session.get('gplus_id'):
            return responseHelper('Current user is already connected.', 200)
    else:
        return getUserInfoAndCreateSession()


def getUserInfoAndCreateSession():
        url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        response = requests.get(url, params=params)
        data = response.json()
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = credentials.id_token['sub']
        login_session['name'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']
        login_session['user_id'] = db.getUserBy(login_session).id
        login_session['provider'] = 'google'
        print login_session.get('access_token')
        flash("you are now logged in as %s" % login_session['name'])
        return responseHelper('User successfully connected.', 200)

# DISCONNECT from google
@google_sign_in.route('/gdisconnect')
def gdisconnect():
  print login_session.keys()
  access_token = login_session['access_token']
  print 'In gdisconnect access token is %s', access_token
  print 'User name is: ' 
  print login_session['name']
  if access_token is None:
    print 'Access Token is None'
    response = make_response(json.dumps('Current user not connected.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
    
  url = ('https://accounts.google.com/o/oauth2/revoke?token=%s' 
        % login_session['access_token'])
  h = httplib2.Http()
  result = h.request(url, 'GET')[0]
  print 'result is '
  print result
    
  if result['status'] == '200': 
    del login_session['gplus_id']
    del login_session['name']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response
  
  else:
    response = make_response(json.dumps('Failed to revoke token.', 400))
    response.headers['Content-Type'] = 'application/json'
    return response
