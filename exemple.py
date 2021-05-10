import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from table_creater import *


engine = create_engine('sqlite:///BD/users.db', echo=True)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()


user = User(username="python",password="python",email="69@69.com")
session.add(user)

# commit the record the database
session.commit()

session.commit()