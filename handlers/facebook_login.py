import httplib2
import requests
import json
from itemcatalog_db_helper import *
from handlers.utility_methods import checkAuthorizedState, responseHelper
from handlers.utility_methods import setCredentials, storeTokenInfo, getUserID
from flask import Flask, flash, make_response, Blueprint, request, url_for
from flask import session as login_session

TEMPLDIR = "../templates"
NAME = "facebook_login"

facebook_login = Blueprint(NAME, __name__, template_folder=TEMPLDIR)

db = DBHelper()


# oAuth Flow and Error Checking for Facebook
@facebook_login.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
    Gathers data from Facebook Sign In API and places it inside a
    session variable.
    """
    return checkIfFacebookAuthorized(request)


def checkIfFacebookAuthorized(client_request):
    """
    Check if the state is Valid
    """
    if not checkAuthorizedState(client_request.args.get('state')):
        return responseHelper('Invalid authentication paramaters.', 401)
    else:
        access_token = client_request.data
        print "access token received %s " % access_token
        return tryFacebookFlow(access_token)


def tryFacebookFlow(access_token):
    """
    Exchange access token and store Facebook variables
    """
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
    """
    Get the Facebook picture and store as a session variable
    """
    url = "https://graph.facebook.com/v2.4/me/picture?"
    url += ("%s&redirect=0&height=200&width=200"
            % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]
    return checkFacebookUserAndCreateSession()


def checkFacebookUserAndCreateSession():
    """
    See if user exists and return the user's id and stores it in a session
    variable.  If no user exists a user is created.
    """
    user_id = db.getUserID(login_session['email'])
    if not user_id:
        user_id = db.createUser(login_session)
    db.updatePicture(login_session)
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


@facebook_login.route('/fbdisconnect')
def fbdisconnect():
    """
    Delete's facebook's session variables and returns appropriate response
    """
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
