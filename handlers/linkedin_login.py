import httplib2
import requests
import json
from itemcatalog_db_helper import *
from handlers.utility_methods import checkAuthorizedState, responseHelper, setCredentials, storeTokenInfo, getUserID
from flask import Flask, flash, make_response, Blueprint, request, redirect, url_for, session as login_session

linkedin_login = Blueprint("linkedin_login", __name__, template_folder="../templates")

db = DBHelper()

# oAuth Flow and Error Checking for LinkedIn
@linkedin_login.route('/callback/linkedin', methods=['GET'])
def linkedincallback():
  source = 'ln_client_secrets.json'
  code = request.args.get('code')
  request_state = request.args.get('state')
  login_state = login_session['state']
  return_uri = 'http://item-catalogue.dev:5500/callback/linkedin'
  client_id = json.loads(open(source, 'r').read())['web']['app_id']
  client_secret = json.loads(open(source, 'r').read())['web']['app_secret']

  if request_state != login_state:
    response = make_response(json.dumps('Invalid state parameter.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  url = "https://www.linkedin.com/oauth/v2/accessToken"
  url += "?grant_type=authorization_code&code="
  url += ("%s&client_id=%s&client_secret=%s&redirect_uri=%s" 
          % (code, client_id, client_secret, return_uri))

  h = httplib2.Http()
  result = h.request(url, 'GET')[1]
  access_token = result.split('\"')[3]
  login_session['access_token'] = access_token
  

  userinfo_url = "https://api.linkedin.com/v1/people/~:(id,email-address,"
  userinfo_url += "first-name,last-name,picture-url)"
  userinfo_url += ("?format=json&oauth2_access_token=%s" 
                  % login_session['access_token'])

  h = httplib2.Http()
  result_data = h.request(userinfo_url, 'GET')[1]
  data = json.loads(result_data)


  first_name = data["firstName"] 
  last_name = data["lastName"]
  login_session['name'] = first_name + " " + last_name
  login_session['email'] = data["emailAddress"]
  login_session['user_id'] = data["id"]
  login_session['picture'] = data["pictureUrl"]
  login_session['provider'] = 'linkedin'


  # see if user exists
  user_id = getUserID(login_session['email'])
  if not user_id:
    user_id = db.createUser(login_session)
  

  db.updatePicture(login_session)
  user = db.getUser(login_session['email'])
  login_session['user_id'] = user.id
  flash("Now logged in as %s" % login_session['name'])
  print user.picture
  #return output
  return redirect('/')
  
@linkedin_login.route('/lidisconnect')
def lidisconnect():
    print login_session.keys()
    access_token = login_session['access_token']
    print 'In liisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['name']
    if access_token is None:
      print 'Access Token is None'
      response = make_response(json.dumps('Current user not connected.'), 401)
      response.headers['Content-Type'] = 'application/json'
      return response
    
    if access_token: 
      del login_session['name']
      del login_session['email']
      del login_session['picture']
      del login_session['user_id']
      del login_session['access_token']
      
      response = make_response(json.dumps('Successfully disconnected.'), 200)
      response.headers['Content-Type'] = 'application/json'
      return response
    
    else:
      response = make_response(json.dumps('Failed to revoke token', 400))
      response.headers['Content-Type'] = 'application/json'
      return response
