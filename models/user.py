from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

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