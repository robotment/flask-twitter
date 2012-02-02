from database import db_session
from models import Tweet
#print repr(Tweet.query.all()[0])
print len(Tweet.query.all())
