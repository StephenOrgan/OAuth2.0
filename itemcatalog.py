import json
import httplib2
import requests
import string
import random
import os
import requests
from urlparse import urlparse

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from flask import redirect, request, render_template, flash
from flask import Flask, url_for, session as login_session
from flask import jsonify, make_response, send_from_directory
from itemcatalog_db_setup import Item
from itemcatalog_db_helper import *
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from itemcatalog_db_setup import Base, Category, Item, User
from werkzeug.utils import secure_filename

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = DBHelper()

G_SOURCE = 'client_secrets.json'
LI_SOURCE = 'ln_client_secrets'

G_CID = json.loads(open(G_SOURCE, 'r').read())['web']['client_id']
LI_ID = json.loads(open(LI_SOURCE, 'r').read())['web']['app_id']
LI_SECRET = json.loads(open(LI_SOURCE, 'r').read())['web']['app_secret']
LI_RET_URI = json.loads(open(LI_SOURCE, 'r').read())['web']['return_uri']
LI_SCOPE = "r_basicprofile r_emailaddress"


# Static Pages
@app.route('/')
@app.route('/category/')
def showCategories():
    createSession()
    categories = db.getIndexCategories()
    latestItems = db.getLatestItems()
    return render_template('category-index.html',
                           categories=categories,
                           items=latestItems,
                           user_id=login_session.get('user_id'),
                           STATE=login_session.get('state'))


@app.route('/category/<int:category_id>/')
def showItemsByCategory(category_id):
    createSession()
    categories = db.getIndexCategories()
    category = db.getByCategory(category_id)
    items = db.getItemsByCategory(category_id)
    return render_template('category.html',
                           main_category=category,
                           categories=categories,
                           category_id = category_id,
                           items=items,
                           user_id=login_session.get('user_id'),
                           STATE=login_session.get('state'))


@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(category_id, item_id):
    createSession()
    categories = db.getIndexCategories()
    item = db.getByItem(item_id)
    return render_template('item.html',
                           categories=categories,
                           item=item,
                           main_category=category_id,
                           user_id=login_session.get('user_id'),
                           STATE=login_session.get('state'),
                           category_id = category_id)

@app.route('/login')
def showLogin():
    createSession()
    login_state = login_session['state']
    linkedinurl = "https://www.linkedin.com/uas/oauth2/authorization"
    linkedinurl += "?response_type=code&client_id="
    linkedinurl += "%s&scope=%s&state=%s&redirect_uri=%s" % (LI_ID, LI_SCOPE, 
                                                      login_state, LI_RET_URI)

    return render_template('login2.html', STATE=login_session['state'], 
                          linkedinurl=linkedinurl)



# CRUD

@app.route('/addItem', methods=['GET','POST'])
def addItemWithoutCategory(category_id=None):
  createSession()
  categories = db.getIndexCategories()
  category_identifier = request.args.get('category_id')
  category = None
  
  if category_identifier:
    category = db.getByCategory(category_identifier)
  if 'name' not in login_session:
        return redirect(url_for('showLogin'))
  if not category_id and request.method != 'POST':
    return render_template('newitemwithPicklist.html', 
                          STATE=login_session['state'], categories=categories, 
                          category=category)
  
  if request.method == 'POST':
    if checkAuthorizedState(request.form['state']) is False:
      return responseWith('Invalid authorization paramaters.', 401)  
    if validitem():
      saveItemWithPicture(request.form['category_id'])
      return redirect(url_for('showItemsByCategory', 
                      category_id = request.form['category_id']))
    else:
        return render_template('newitemwithPicklist.html', 
                              STATE=login_session['state'], 
                              categories=categories)

def validitem():
  name = request.form['name']
  description = request.form['description']
  category_id = request.form['category_id']
  newfile = request.files['file']

  if name and description and category_id and newfile:
    return True
  else:
    return None

@app.route('/category/<int:category_id>/addItem', methods=['GET', 'POST'])
def addItemToCategory(category_id):
    createSession()
    category = db.getByCategory(category_id)
    
    if 'name' not in login_session:
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
      if checkAuthorizedState(request.form['state']) is False:
        return responseWith('Invalid authorization paramaters.', 401)
      if validitem_nocategory():
        saveItemWithPicture(category.id)
        return redirect(url_for('showItemsByCategory', 
                        category_id = category.id))
      else: 
        return render_template('newitem.html', category_id = category.id, 
                              category=category, STATE=login_session['state'])
    else:
        return render_template('newitem.html', category_id = category.id, 
                              category=category, STATE=login_session['state'])

def validitem_nocategory():
  name = request.form['name']
  description = request.form['description']
  newfile = request.files['file']

  if name and description and newfile:
    return True
  else:
    return None

def saveItemWithPicture(category_id):
  print ('uploading file...') 
  file = request.files['file']
        
  if file and allowed_file(file.filename):
    filename = secure_filename(file.filename)
    print 'saving file...'
    print (os.path.join(app.config['UPLOAD_FOLDER'], filename))
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    print 'upload complete!'
    
  login_user_id = login_session['user_id']
  newItem = Item(
    name = request.form['name'], 
    description = request.form['description'], 
    image_url = filename, 
    category_id = category_id,
    user_id = login_user_id)
  db.addToDb(newItem)
  flash('New Item:  %s, Successfully Created' % (newItem.name))
  

@app.route('/category/<int:category_id>/editItem/<int:item_id>/', 
          methods=['GET', 'POST'])
def editItem(category_id, item_id):
  createSession()
  editedItem = db.getItem(item_id)
  category = db.getByCategory(category_id)
  output = "<script>function myFunction() {alert('You are not authorized to"
  output += "edit this item.');}</script><body onload='myFunction()''>"
  print editedItem.name
  
  if 'name' not in login_session:
    return redirect('/login')
  if editedItem.user_id != login_session['user_id']:
    return output
  if request.method == 'POST':
    if checkAuthorizedState(request.form['state']) is False:
      return responseHelper('Invalid authorization paramaters.', 401)

    print 'Checking to see if we have a new file.'
    if request.files['file']:
      file = request.files['file']
      if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], editedItem.image_url))
        editedItem.image_url = filename
      else:
        return responseHelper('Bad Image', 422)
    
    if request.form['name']:
      editedItem.name = request.form['name']
    if request.form['description']:
      editedItem.description = request.form['description']
        
    db.addToDb(editedItem)
    flash('Item Successfully Edited')
    return redirect(url_for('showItem', category_id = category_id, 
                    item_id = item_id))
    
  else:
    return render_template('editItem.html', category = category, 
                          item_id = item_id, item = editedItem, 
                          STATE=login_session['state'])




@app.route('/category/<int:category_id>/deleteItem/<int:item_id>/', 
          methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
  createSession()
  category = db.getByCategory(category_id)
  output = "<script>function myFunction() {alert('You are not authorized to"
  output += "delete this menu item.');}</script><body onload='myFunction()''>"

  itemToDelete = db.getItem(item_id)
    
  if 'name' not in login_session:
    return redirect('/login')
  if itemToDelete.user_id != login_session['user_id']:
    return output
  if request.method == 'POST':
    if checkAuthorizedState(request.form['state']) is False:
      return responseHelper('Invalid authorization paramaters.', 401)
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], itemToDelete.image_url))
    db.deleteFromDb(itemToDelete)
    flash('Item Successfully Deleted')
    return redirect(url_for('showItemsByCategory', category_id = category_id))
  else:
    return render_template('deleteItem.html', item = itemToDelete, 
                          category=category, STATE=login_session['state'])



# oAuth Flow and Error Checking for Google
@app.route('/gconnect', methods=['POST'])
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
@app.route('/gdisconnect')
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


# oAuth Flow and Error Checking for Facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
  return checkIfFacebookAuthorized(request)

def checkIfFacebookAuthorized(client_request):
  if not checkAuthorizedState(client_request.args.get('state')):
    return responseHelper('Invalid authentication paramaters.', 401)
  else:
    access_token = client_request.data
    print "access token received %s " % access_token
    return tryFacebookFlow(access_token)

def tryFacebookFlow(access_token):
  source = 'fb_client_secrets.json'
  app_id = json.loads(open(source, 'r').read())['web']['app_id']
  app_secret = json.loads(open(source, 'r').read())['web']['app_secret']
  url = "https://graph.facebook.com/oauth/access_token"
  url += "?grant_type=fb_exchange_token&client_id="
  url += ("%s&client_secret=%s&fb_exchange_token=%s" 
          % (app_id, app_secret, access_token))
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]
  data = json.loads(result)
  token = 'access_token=' + data['access_token']
  stored_token = token.split("=")[1]
  login_session['access_token'] = stored_token


  url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]
  data = json.loads(result)
  login_session['provider'] = 'facebook' 
  login_session['name'] = data['name']
  login_session['email'] = data['email']
  login_session['facebook_id'] = data['id']
  return getFacebookPicture(token)

def getFacebookPicture(token):
    # Get user picture
    url = "https://graph.facebook.com/v2.4/me/picture?"
    url += ("%s&redirect=0&height=200&width=200" 
            % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]
    return checkFacebookUserAndCreateSession()

def checkFacebookUserAndCreateSession():
    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    #updatePicture(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['name']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;'
    output += 'border-radius: 150px;-webkit-border-radius: '
    output += '150px;-moz-border-radius: 150px;"> '
    flash("Now logged in as %s" % login_session['name'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
  facebook_id = login_session['facebook_id']
  url = 'https://graph.facebook.com/%s/permissions' % facebook_id
  h = httplib2.Http()
  result = h.request(url, 'DELETE')[1]
  del login_session['name']
  del login_session['email']
  del login_session['picture']
  del login_session['user_id']
  del login_session['facebook_id']
  return "you have been logged out"


# oAuth Flow and Error Checking for LinkedIn
@app.route('/callback/linkedin', methods=['GET'])
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
    user_id = DBHelper.createUser(login_session)
  

  DBHelper.updatePicture(login_session)
  user = getUser(login_session['email'])
  login_session['user_id'] = user.id
  flash("Now logged in as %s" % login_session['name'])
  print user.picture
  #return output
  return redirect('/')
  
@app.route('/lidisconnect')
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


# Disconnect depending on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        print login_session['provider']
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['access_token']
            flash("You have successfully been logged out.")
            return redirect(url_for('showCategories'))
            #del login_session['provider']
        if login_session['provider'] == 'facebook':
          fbdisconnect()
          del login_session['provider']
          flash("You have successfully been logged out.")
          return redirect(url_for('showCategories'))
        if login_session['provider'] == 'linkedin':
          lidisconnect()
          del login_session['provider']
          flash("You have successfully been logged out.")
          return redirect(url_for('showCategories'))
        else:
          flash("You were not logged in")
          return redirect(url_for('showCategories'))

#####


#Utility Methods

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


if __name__ == "__main__":
  app.secret_key = 'the_most_sEcReTest-KEy_in_The_wOrLD'
  app.debug = True
  app.run(host='0.0.0.0', port=5500)



