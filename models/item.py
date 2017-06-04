from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from models.category import Category
from models.user import User

Base = declarative_base()

class Item(Base):
  __tablename__ = 'items'
  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)
  description = Column(String, nullable=False)
  image_url = Column(String, nullable=False)
  category_id = Column(Integer, ForeignKey(Category.id), nullable = False)
  item_category = relationship(Category)
  user_id = Column(Integer, ForeignKey(User.id), nullable = False)
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