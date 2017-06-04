from itemcatalog_db_helper import *
from handlers.utility_methods import *

db = DBHelper()

@app.route('/addItem', methods=['GET','POST'])
@login_required
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
      return redirect(url_for('showItemsByCategory', 
                      category_id = request.form['category_id']))
  else:
    if category_identifier:
      category = db.getByCategory(category_identifier)

    if category:
      print "why isn't this working?"
      return render_template('newitem.html', 
                          STATE=login_session['state'], categories=categories, 
                          category=category)

    if not category_id:
      return render_template('newitemwithPicklist.html', 
                              STATE=login_session['state'], 
                              categories=categories)