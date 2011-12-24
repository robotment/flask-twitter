#!/usr/bin/env python
# encoding: utf-8
"""
flaskr_blog.py

Created by Delai on 2011-11-09.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
import os, logging
import __init__ as flaskr
import unittest
import tempfile
import date_util
from flask import Markup, Flask, request

from flask import template_rendered
from contextlib import contextmanager

INDEX_URL= 'http://localhost:5000'

class test(unittest.TestCase):
    def setUp(self):
        self.db_fp, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        flaskr.app.logger.handlers[0].setLevel(logging.INFO)
        self.client = flaskr.app.test_client()
        flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fp)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.client.get('/')
        assert 'No entries here so far' in rv.data

    def test_request(self):
        app1 = Flask(__name__)
        with app1.test_request_context('/delai?age=12'):
            assert request.path == '/delai'
            assert request.url == 'http://localhost/delai?age=12'
            assert request.base_url == 'http://localhost/delai'
            assert request.url_root == 'http://localhost/'      #the full url root (with hostname), this is the application root
            assert request.host_url == 'http://localhost/'   #just the host with scheme
            assert request.query_string == 'age=12'

    def test_redirect(self):
        ctx = flaskr.app.test_request_context('/?next=%s/delai' % INDEX_URL)
        ctx.push()
        flaskr.app.preprocess_request()
        flaskr.app.process_response(flaskr.app.response_class())  # to shutdown a request
        assert flaskr.redirect_url() == "http://localhost:5000/delai"
        ctx.pop()
        
    def login_valide(self, username, password):
        return self.client.post("/login_valide", data=dict(username=username, password=password), follow_redirects = True)

    def logout(self):
        return self.client.get("/logout", follow_redirects = True)

    def test_add_user_action(self):
        #delete user 'delai' first
        from database import db_session
        from models import User
        User.query.filter(User.name == 'delai').delete()
        db_session.commit()
        rv = self.client.post('/add_user', data = dict(username = 'delai', password = '123456', email = 'to.too@qq.com'), follow_redirects = True)
        assert 'Register Successfull for <a href="/delai">@delai</a>' in rv.data, rv.data

    def test_login_and_logout(self):
        #logout first
        rv = self.logout()
        #login page display
        rv = self.client.get('/login.html', follow_redirects = True)
        assert '<form action="/login_valide"' in rv.data, rv.data
        
        #login action
        rv = self.login_valide('notuser', 'the pas')
        assert 'No User Named' in rv.data

        rv = self.login_valide('delai', 'ddddd')
        assert 'Invalid Password' in rv.data

        rv = self.login_valide('delai', '123456')
        assert 'You has log in successfully' in rv.data

        #logout redirect to index page
        rv = self.logout()
        assert 'You were logged out' in rv.data
        assert 200 == rv.status_code
  
        #logout while not logged in
        rv = self.logout()
        assert 'You have not login right now' in rv.data

    def test_add_entry(self):
        username = 'delai'
        self.login_valide(username, '123456')
        rv = self.client.post('/add_entry', data=dict(author=username, title='<Hello>', text='<strong>HTML</strong> allowed here', redirect_url=INDEX_URL), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert 'New entry is successfully added' in rv.data, rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data
        
    def test_register_page(self):
        rv = self.client.get('/register.html', follow_redirects = True)
        assert '<h2>Register</h2>' in rv.data
        assert '<form action="/add_user" method="post" accept-charset="utf-8">' in rv.data

    def test_login_required_decorator(self):
        assert 'add entry action' in flaskr.add_entry.__doc__ , flaskr.add_entry.__doc__
        assert flaskr.add_entry.__name__ == 'add_entry', flaskr.add_entry.__name__

if __name__ == '__main__':
    unittest.main()
