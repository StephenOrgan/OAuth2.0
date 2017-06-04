from itemcatalog_db_helper import *
from handlers.utility_methods import *

db = DBHelper()

@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(category_id, item_id):
    createSession()
    categories = db.getIndexCategories()
    item = db.getByItem(item_id)
    return render_template('item.html',
                           categories=categories,
                           item=item,
                           main_category=category_id,
                           user_id=login_session.get('user_id'),
                           STATE=login_session.get('state'),
                           category_id = category_id)

# serialized JSON
@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def ItemJSON(category_id, item_id):
    item = db.getItem(item_id)
    return jsonify(Item = item.serialize)

