import json
from itemcatalog_db_helper import *
from handlers.utility_methods import login_required, createSession
from handlers.utility_methods import checkAuthorizedState
from flask import redirect, request, render_template, flash, Blueprint
from flask import Flask, url_for, session as login_session

login = Blueprint("login", __name__, template_folder="../templates")

db = DBHelper()

LI_SOURCE = 'ln_client_secrets.json'
LI_ID = json.loads(open(LI_SOURCE, 'r').read())['web']['app_id']
LI_ID = json.loads(open(LI_SOURCE, 'r').read())['web']['app_id']
LI_SECRET = json.loads(open(LI_SOURCE, 'r').read())['web']['app_secret']
LI_RET_URI = json.loads(open(LI_SOURCE, 'r').read())['web']['return_uri']
LI_SCOPE = "r_basicprofile r_emailaddress"


@login.route('/login')
def showLogin():
    createSession()
    login_state = login_session['state']
    user_id = login_session.get('user_id')
    linkedinurl = "https://www.linkedin.com/uas/oauth2/authorization"
    linkedinurl += "?response_type=code&client_id="
    linkedinurl += "%s&scope=%s&state=%s&redirect_uri=%s" % (LI_ID, LI_SCOPE,
                                                             login_state,
                                                             LI_RET_URI)

    return render_template('login2.html', STATE=login_session['state'],
                           linkedinurl=linkedinurl, user_id=user_id)
