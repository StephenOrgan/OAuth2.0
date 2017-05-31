from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
  __tablename__ = 'user'
  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable=False)
  email = Column(String(250), nullable=False)
  picture = Column(String(250))

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
      'name'         : self.name,
      'id'           : self.id,
      'email'        : self.email,
    }

class Category(Base):
  __tablename__ = 'categories'
  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)

  @property
  def serialize(self):
    return {
      'id': self.id,
      'name': self.name,
    }

class Item(Base):
  __tablename__ = 'items'
  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)
  description = Column(String, nullable=False)
  image_url = Column(String, nullable=False)
  category_id = Column(Integer, ForeignKey('categories.id'), nullable = False)
  item_category = relationship(Category)
  user_id = Column(Integer, ForeignKey('user.id'), nullable = False)
  user = relationship(User)

  @property
  def serialize(self):
    return {
      'id': self.id,
      'name': self.name,
      'image_url': self.image_url,
      'description': self.description,
      'category.id': self.category_id
    }

engine = create_engine('sqlite:///item_catalogue.db')

Base.metadata.create_all(engine)