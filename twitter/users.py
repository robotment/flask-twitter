#!/user/bin/python2.7

from database import db_session
from models import User

def user_valide(username, password):
    message = []
    approved = False
    u = User.query.filter_by(name = username).first()
    if not u:
        message.append('No User Named ' + username)
    elif u.password != password:
        message.append('Invalid Password')
    else:
        message = None
        approved = True
    return approved, message

def is_user(username):
    if User.query.filter_by(name = username).first():
        return True
    else:
        return False

if __name__ == '__main__':
    approved, message = user_valide('shidelai', 'shizai')
    assert approved == True
    assert message == None
    
    assert True == is_user('shidelai')
    assert False == is_user('sidelai')
