from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
 
Base = declarative_base()

from models.user import User
from models.category import Category
from models.item import Item

engine = create_engine('sqlite:///item_catalogue.db')

Base.metadata.create_all(engine)