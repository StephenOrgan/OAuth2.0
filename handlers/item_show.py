import os
from itemcatalog_db_helper import *
from handlers.utility_methods import login_required, createSession
from handlers.utility_methods import checkAuthorizedState
from flask import redirect, request, jsonify, render_template, flash, Blueprint
from flask import Flask, url_for, session as login_session

itemshow = Blueprint("itemshow", __name__, template_folder="../templates")

db = DBHelper()


@itemshow.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(category_id, item_id):
    """
    Create a new session if the user isn't logged in and render the
    template to show the individual item.
    """
    createSession()
    categories = db.getIndexCategories()
    item = db.getByItem(item_id)
    return render_template('item.html',
                           categories=categories,
                           item=item,
                           main_category=category_id,
                           user_id=login_session.get('user_id'),
                           STATE=login_session.get('state'),
                           category_id=category_id)


# serialized JSON
@itemshow.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def ItemJSON(category_id, item_id):
    """
    Return a serialized JSON result for the individual item.
    """
    item = db.getItem(item_id)
    return jsonify(Item=item.serialize)
