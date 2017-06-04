from itemcatalog_db_helper import *
from handlers.utility_methods import *

db = DBHelper()

@app.route('/')
@app.route('/category/')
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
@app.route('/category/JSON')
def categoriesJSON():
    categories = db.getIndexCategories()
    return jsonify(categories= [c.serialize for c in categories])
