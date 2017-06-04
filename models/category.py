from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


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