from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///BD/users.db', echo=True)
Base = declarative_base()

########################################################################
class User(Base):

	__tablename__ = "users"
	user_id=Column(Integer, primary_key=True, autoincrement=True)
	username=Column(String(25), nullable=False, info='')
	password=Column(String(25), nullable=False, info='')
	email=Column(String(25), nullable=False, info='')




#----------------------------------------------------------------------
def __init__(self, username, password,email):

	self.username = username
	self.password = password
	self.email=email

# create tables
Base.metadata.create_all(engine)