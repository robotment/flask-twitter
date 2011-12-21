#!/user/bin/python2.7

users = {'shidelai': '123456',
        'jialiang': '123456',
        'bobo': '123456'}

def user_valide(username, password):
    message = []
    approved = False
    if username not in users:
        message.append('No User Named ' + username)
    elif password != users[username]:
        message.append('Invalid Password')
    else:
        message = None
        approved = True
    return approved, message

def is_user(username):
	if username in users:
		return True
	else:
		return False

if __name__ == '__main__':
    approved, message = user_valide('shidelai', 'shizai')
    assert approved == True
    assert message == None
    
    assert True == is_user('shidelai')
    assert False == is_user('sidelai')
