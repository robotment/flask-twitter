#!/usr/bin/env python
# encoding: utf-8
"""
flaskr_blog.py

Created by lailai on 2011-11-09.
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
from database import db_session
from models import User, Tweet

INDEX_URL= 'http://localhost:5000'

class test(unittest.TestCase):
    def setUp(self):
        self.db_fp, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        flaskr.app.logger.handlers[0].setLevel(logging.INFO)
        self.client = flaskr.app.test_client()

    def tearDown(self):
        os.close(self.db_fp)
        os.unlink(flaskr.app.config['DATABASE'])

    def delete_lailai(self):
        User.query.filter(User.name == 'lailai').delete()
        Tweet.query.filter_by(author = 'lailai').delete()
        db_session.commit()
    
    def add_lailai(self):
        return self.client.post('/add_user', data = dict(username = 'lailai', password = '123456', email = 'to.too@qq.com'), follow_redirects = True)

    def test_not_exist_user_page(self):
        self.delete_lailai()
        rv = self.client.get('/lailai')
        assert '404' in rv.data

    def test_register_page(self):
        rv = self.client.get('/register.html', follow_redirects = True)
        assert '<h2>Register</h2>' in rv.data
        assert '<form action="/add_user" method="post" accept-charset="utf-8">' in rv.data

    def test_add_user_action(self):
        self.delete_lailai()
        rv = self.add_lailai()
        assert 'Register Successfull for <a href="/lailai">@lailai</a>' in rv.data, rv.data

    def test_user_has_no_tweet(self):
        self.delete_lailai()
        self.add_lailai()
        rv = self.client.get('/lailai')
        assert 'No tweets here so far' in rv.data, rv.data

    def test_add_tweet(self):
        self.add_lailai()
        username = 'lailai'
        self.login_valide(username, '123456')
        rv = self.client.post('/add_tweet', data=dict(author=username, title='<Hello>', text='<strong>HTML</strong> allowed here', redirect_url=INDEX_URL), follow_redirects=True)
        assert 'No tweets here so far' not in rv.data
        assert 'New tweet is successfully added' in rv.data, rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data


    def test_request(self):
        app1 = Flask(__name__)
        with app1.test_request_context('/lailai?age=12'):
            assert request.path == '/lailai'
            assert request.url == 'http://localhost/lailai?age=12'
            assert request.base_url == 'http://localhost/lailai'
            assert request.url_root == 'http://localhost/'      #the full url root (with hostname), this is the application root
            assert request.host_url == 'http://localhost/'   #just the host with scheme
            assert request.query_string == 'age=12'

    def test_redirect(self):
        ctx = flaskr.app.test_request_context('/?next=%s/lailai' % INDEX_URL)
        ctx.push()
        flaskr.app.preprocess_request()
        flaskr.app.process_response(flaskr.app.response_class())  # to shutdown a request
        assert flaskr.redirect_url() == "http://localhost:5000/lailai"
        ctx.pop()
        
    def login_valide(self, username, password):
        return self.client.post("/login_valide", data=dict(username=username, password=password), follow_redirects = True)

    def logout(self):
        return self.client.get("/logout", follow_redirects = True)

    def test_login_and_logout(self):
        self.add_lailai()
        #logout first
        rv = self.logout()
        #login page display
        rv = self.client.get('/login.html', follow_redirects = True)
        assert '<form action="/login_valide"' in rv.data, rv.data
        
        #login action
        rv = self.login_valide('notuser', 'the pas')
        assert 'No User Named' in rv.data

        rv = self.login_valide('lailai', 'ddddd')
        assert 'Invalid Password' in rv.data

        rv = self.login_valide('lailai', '123456')
        assert 'You has log in successfully' in rv.data

        #logout redirect to index page
        rv = self.logout()
        assert 'You were logged out' in rv.data
        assert 200 == rv.status_code
  
        #logout while not logged in
        rv = self.logout()
        assert 'You have not login right now' in rv.data


        


    def test_login_required_decorator(self):
        assert 'add tweet action' in flaskr.add_tweet.__doc__ , flaskr.add_tweet.__doc__
        assert flaskr.add_tweet.__name__ == 'add_tweet', flaskr.add_tweet.__name__

if __name__ == '__main__':
    unittest.main()
