from itemcatalog_db_helper import *
from handlers.utility_methods import *

db = DBHelper()

@app.route('/login')
def showLogin():
    createSession()
    login_state = login_session['state']
    linkedinurl = "https://www.linkedin.com/uas/oauth2/authorization"
    linkedinurl += "?response_type=code&client_id="
    linkedinurl += "%s&scope=%s&state=%s&redirect_uri=%s" % (LI_ID, LI_SCOPE, 
                                                      login_state, LI_RET_URI)

    return render_template('login2.html', STATE=login_session['state'], 
                          linkedinurl=linkedinurl, user_id=login_session.get('user_id'))