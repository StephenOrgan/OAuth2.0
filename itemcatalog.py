from flask import Flask
from itemcatalog_db_helper import *
from itemcatalog_db_setup import Base, Category, Item, User

# static URL handlers
from handlers.category_index import cat
from handlers.category_items import item
from handlers.item_show import itemshow
from handlers.login import login
from handlers.disconnect import logout

# CRUD
from handlers.item_new import newitem
from handlers.item_edit import item_edit
from handlers.item_delete import item_delete

# OAUTH PROVIDERS
from handlers.google_sign_in import google_sign_in, gdisconnect
from handlers.facebook_login import facebook_login, fbdisconnect
from handlers.linkedin_login import linkedin_login, lidisconnect


app = Flask(__name__)
app.register_blueprint(cat)
app.register_blueprint(item)
app.register_blueprint(newitem)
app.register_blueprint(itemshow)
app.register_blueprint(login)
app.register_blueprint(item_edit)
app.register_blueprint(item_delete)
app.register_blueprint(google_sign_in)
app.register_blueprint(facebook_login)
app.register_blueprint(linkedin_login)
app.register_blueprint(logout)

db = DBHelper()


if __name__ == "__main__":
  app.secret_key = 'the_most_sEcReTest-KEy_in_The_wOrLD'
  app.debug = True
  app.run(host='0.0.0.0', port=5500)