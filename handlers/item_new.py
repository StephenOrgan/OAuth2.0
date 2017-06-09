import os
from itemcatalog_db_helper import *
from handlers.utility_methods import login_required, createSession
from handlers.utility_methods import checkAuthorizedState, allowed_file
from flask import redirect, request, render_template, flash, Blueprint
from flask import Flask, url_for, session as login_session
from werkzeug.utils import secure_filename

DOWNDIR = '..'
EXTENSION = 'static/uploads'
DIRNAME = os.path.dirname(__file__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = os.path.abspath(os.path.join(DIRNAME, DOWNDIR, EXTENSION))

newitem = Blueprint("newitem", __name__, template_folder="../templates")

db = DBHelper()


@login_required
@newitem.route('/addItem', methods=['GET', 'POST'])
def addItemWithoutCategory(category_id=None):
    """
    Create a new session if the user isn't logged in.
    For POST requests, if the item variables are valid will save a new
    item into the db.  For GET requets we check whether the user is under
    a category and add render the form for that category. If there is no
    category then the user will need to define a category from a picklist.
    """
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
                            category_id=request.form['category_id']))
    else:
        if category_identifier:
            category = db.getByCategory(category_identifier)

        if category:
            return render_template('newitemwithPicklist.html',
                                   STATE=login_session['state'],
                                   categories=categories,
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
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    login_user_id = login_session['user_id']
    newItem = Item(
        name=request.form['name'],
        description=request.form['description'],
        image_url=filename,
        category_id=category_id,
        user_id=login_user_id)
    db.addToDb(newItem)
    flash('New Item:  %s, Successfully Created' % (newItem.name))
