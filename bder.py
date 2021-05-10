from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from table_creater import *

Session = sessionmaker(bind=engine)
s = Session()


def login(username,password):



	return(bool(s.query(User).filter_by(username=username,password=password).first()) )

def id(username,password):

	if login(username,password):
		s.query(User).filter_by(username=username,password=password)