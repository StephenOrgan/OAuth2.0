from itemcatalog_db_helper import *
from handlers.utility_methods import *

db = DBHelper()

@app.route('/category/<int:category_id>/')
def showItemsByCategory(category_id):
    createSession()
    categories = db.getIndexCategories()
    category = db.getByCategory(category_id)
    items = db.getItemsByCategory(category_id)
    return render_template('category.html',
                           main_category=category,
                           categories=categories,
                           category_id = category_id,
                           items=items,
                           user_id=login_session.get('user_id'),
                           STATE=login_session.get('state'))


# serialized JSON
@app.route('/category/<int:category_id>/JSON')
def categoryItemJSON(category_id):
    category = db.getByCategory(category_id)
    items = db.getItemsByCategory(category_id)
    return jsonify(Items=[i.serialize for i in items])