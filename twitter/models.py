'''
SQLAlchemy in Flask
'''
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    password = Column(String(20))
    email = Column(String(40))

    def __init__(self, name=None, password = None, email=None):
        self.name = name
        self.email = email
        self.password = password
    def __repr__(self):
        return "User: %s PassWord: %s Email: %s" % (self.name, self.password, self.email)


