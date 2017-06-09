import os
from itemcatalog_db_helper import *
from handlers.utility_methods import login_required, createSession, checkAuthorizedState, allowed_file
from flask import redirect, request, render_template, flash, Blueprint, current_app as app
from flask import Flask, url_for, session as login_session
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'static/uploads'))

newitem = Blueprint("newitem", __name__, template_folder="../templates")

db = DBHelper()

@login_required
@newitem.route('/addItem', methods=['GET','POST'])
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
      return redirect(url_for('itemforcategory.showItemsByCategory', 
                      category_id = request.form['category_id']))
  else:
    if category_identifier:
      category = db.getByCategory(category_identifier)

    if category:
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

def saveItemWithPicture(category_id):
  print ('uploading file...') 
  file = request.files['file']
        
  if file and allowed_file(file.filename):
    filename = secure_filename(file.filename)
    print 'saving file...'
    file.save(os.path.join(UPLOAD_FOLDER, filename))
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

