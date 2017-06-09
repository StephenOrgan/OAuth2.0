from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from itemcatalog_db_setup import Base, Category, Item, User


engine = create_engine('sqlite:///item_catalogue.db')
Base.metadata.bind = engine
database_session = sessionmaker(bind=engine)
session = database_session()

class DBHelper:
  def addUser(self, auth_session):
    newUser = User(name=auth_session['name'], email=auth_session['email'],
                   picture=auth_session['picture'])
    session.add(newUser)
    session.commit()
    return

  def getUserBy(self, auth_session):
    try:
      user = session.query(User).filter_by(email=auth_session['email']).first()
      return user
    except:
      self.addUser(auth_session)
      return session.query(User).filter_by(email=auth_session['email']).first()

  def getByCategory(self, category_id):
    return session.query(Category).filter_by(id=category_id).first()

  def getItem(self, item_id):
    return session.query(Item).filter_by(id=item_id).one()

  def getIndexCategories(self):
    return session.query(Category).all()

  def getByItem(self, item_id):
    query = session.query(Item, Category)
    return query.filter_by(id=item_id).join(Category).one()

  def getItemsByCategory(self, category_id):
    return session.query(Item).filter_by(category_id=category_id).all()

  def getLatestItems(self):
    return session.query(Item).limit(10)

  def addToDb(self, new_or_updated_object):
    session.add(new_or_updated_object)
    session.commit()
    return

  def deleteFromDb(self, item):
    session.delete(item)
    session.commit()
    return

  def getUserID(self, email):
    try:
      user = session.query(User).filter_by(email=email).first()
      return user.id
    except:
      return None

  def getUserInfo(self, user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

  def getUser(self, email):
    try:
      user = session.query(User).filter_by(email=email).first()
      return user
    except:
      return None


  @staticmethod
  def createUser(auth_session):
    newUser = User(name=auth_session['name'], email=auth_session['email'],
                   picture=auth_session['picture'])
    session.add(newUser)
    session.commit()
    return

  @staticmethod
  def updatePicture(login_session):
    email = login_session['email']
    updateUser = session.query(User).filter_by(email=email).first()
    updateUser.picture = login_session['picture']
    session.add(updateUser)
    session.commit()
    return updateUser.picture
