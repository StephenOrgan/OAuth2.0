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
UPLOAD_FOLDER = os.path.abspath(os.path.join(DIRNAME, DOWNDIR, EXTENSION))

item_edit = Blueprint("item_edit", __name__, template_folder="../templates")

db = DBHelper()


@login_required
@item_edit.route('/category/<int:category_id>/editItem/<int:item_id>/',
                 methods=['GET', 'POST'])
def editItem(category_id, item_id):
    createSession()
    editedItem = db.getItem(item_id)
    category = db.getByCategory(category_id)
    output = "<script>function myFunction() {alert('You are not authorized to"
    output += "edit this item.');}</script><body onload='myFunction()''>"

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
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                os.remove(os.path.join(UPLOAD_FOLDER, editedItem.image_url))
                editedItem.image_url = filename
            else:
                return responseHelper('Bad Image', 422)

        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']

        db.addToDb(editedItem)
        flash('Item Successfully Edited')
        return redirect(url_for('itemshow.showItem', category_id=category_id,
                        item_id=item_id))

    else:
        return render_template('editItem.html', category=category,
                               item_id=item_id, item=editedItem,
                               STATE=login_session['state'])
