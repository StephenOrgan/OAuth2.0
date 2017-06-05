import requests
from itemcatalog_db_helper import *
from handlers.utility_methods import app, login_required, createSession
from flask import redirect, request, render_template, flash
from flask import Flask, url_for, session as login_session

#app = Flask(__name__, template_folder='../templates')


db = DBHelper()

@app.route('/addItem', methods=['GET','POST'])
@login_required
def addItemWithoutCategory(category_id=None):
  createSession()
  categories = db.getIndexCategories()
  category_identifier = request.args.get('category_id')
  category = None

  
  if request.method == 'POST':
    if checkAuthorizedState(request.form['state']) is False:
      return responseWith('Invalid authorization paramaters.', 401)  
    if validitem():
      saveItemWithPicture(request.form['category_id'])
      return redirect(url_for('showItemsByCategory', 
                      category_id = request.form['category_id']))
  else:
    if category_identifier:
      category = db.getByCategory(category_identifier)

    if category:
      print "render_template is not rendering the template and instead giving me a view error"
      return render_template('newitemwithPicklist.html', 
                          STATE=login_session['state'], categories=categories, 
                          category=category)

    if not category:
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