from itemcatalog_db_helper import *
from handlers.utility_methods import createSession
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash
from flask import session as login_session

cat = Blueprint("category", __name__, template_folder="../templates")

db = DBHelper()


@cat.route('/')
@cat.route('/category/')
def showCategories():
    """
    Create a new session if the user isn't logged in and gather
    all the categories and the latest items to render the
    category index template.
    """
    createSession()
    categories = db.getIndexCategories()
    latestItems = db.getLatestItems()
    return render_template('category-index.html',
                           categories=categories,
                           items=latestItems,
                           user_id=login_session.get('user_id'),
                           STATE=login_session.get('state'))


# serialized JSON
@cat.route('/category/JSON')
def categoriesJSON():
    """
    Return a serialized JSON result for all categories.
    """
    categories = db.getIndexCategories()
    return jsonify(categories=[c.serialize for c in categories])
