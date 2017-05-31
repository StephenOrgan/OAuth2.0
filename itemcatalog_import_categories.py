from itemcatalog_db_setup import Category
from itemcatalog_db_helper import DBHelper

db = DBHelper()
categories_to_insert = [Category(name='Forwards'),
                  Category(name='Defense'),
                  Category(name='Goalies'),
                  Category(name='Coaching Staff'),
                  Category(name='Executive Staff')
                  ]
for category in categories_to_insert:
    db.addToDb(category)