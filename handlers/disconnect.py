from handlers.google_sign_in import gdisconnect
from handlers.facebook_login import fbdisconnect
from handlers.linkedin_login import lidisconnect
from flask import flash, Blueprint, redirect, url_for, session as login_session

logout = Blueprint("logout", __name__, template_folder="../templates")

@logout.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        print login_session['provider']
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['access_token']
            flash("You have successfully been logged out.")
            return redirect(url_for('category.showCategories'))
            #del login_session['provider']
        if login_session['provider'] == 'facebook':
          fbdisconnect()
          del login_session['provider']
          flash("You have successfully been logged out.")
          return redirect(url_for('category.showCategories'))
        if login_session['provider'] == 'linkedin':
          lidisconnect()
          del login_session['provider']
          flash("You have successfully been logged out.")
          return redirect(url_for('category.showCategories'))
        else:
          flash("You were not logged in")
          return redirect(url_for('category.showCategories'))