from itemcatalog_db_helper import *
from utility_methods import createSession
from flask import Blueprint, render_template, redirect, url_for, flash
from flask import session as login_session

cat = Blueprint("category", __name__, template_folder="../templates")

db = DBHelper()

@cat.route('/')
@cat.route('/category/')
def showCategories():
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
    categories = db.getIndexCategories()
    return jsonify(categories= [c.serialize for c in categories])
