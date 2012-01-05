'''
SQLAlchemy in Flask
'''
from sqlalchemy import Column, Integer, String, TIMESTAMP
from database import Base
from date_util import str_from_datetime

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


class Tweet(Base):
    __tablename__ = 'tweet'
    id = Column(Integer, primary_key=True)
    author = Column(String(20), nullable=True)
    text = Column(String(200), nullable=True)
    post_time = Column(TIMESTAMP, nullable=True)

    def __init__(self, author, text, post_time):
        self.author = author
        self.text = text
        self.post_time = post_time
    
    def __repr__(self):
        return u"Tweet: author:%s, text:%s, post_time:%s" % (self.author, self.text, str_from_datetime(self.post_time))
    
    def __str__(self):
        return u"Tweet: author:%s, text:%s, post_time:%s" % (self.author, self.text, str_from_datetime(self.post_time))