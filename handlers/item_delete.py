import os
from itemcatalog_db_helper import *
from handlers.utility_methods import login_required, createSession
from handlers.utility_methods import checkAuthorizedState, allowed_file
from flask import redirect, request, render_template, flash, Blueprint
from flask import Flask, url_for, session as login_session

DOWNDIR = '..'
EXTENSION = 'static/uploads'
DIRNAME = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.abspath(os.path.join(DIRNAME, DOWNDIR, EXTENSION))
NAME = "item_delete"
item_delete = Blueprint(NAME, __name__, template_folder="../templates")

db = DBHelper()


@login_required
@item_delete.route('/category/<int:category_id>/deleteItem/<int:item_id>/',
                   methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    """
    For GET requests the user has to give permission to delete the item.
    For POST requests, check if state is valid and if so, delete any depending
    images from the database and delete the item.  Redirect the user to the
    previous category they were on.
    """
    createSession()
    category = db.getByCategory(category_id)
    output = "<script>function myFunction() {alert('You are not authorized to"
    output += "delete this menu item.');}</script>"
    output += "<body onload='myFunction()''>"

    itemToDelete = db.getItem(item_id)

    if itemToDelete.user_id != login_session['user_id']:
        return output
    if request.method == 'POST':
        if checkAuthorizedState(request.form['state']) is False:
            return responseHelper('Invalid authorization paramaters.', 401)
        os.remove(os.path.join(UPLOAD_FOLDER, itemToDelete.image_url))
        db.deleteFromDb(itemToDelete)
        flash('Item Successfully Deleted')
        return redirect(url_for('itemforcategory.showItemsByCategory',
                        category_id=category_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete,
                               category=category, STATE=login_session['state'])
