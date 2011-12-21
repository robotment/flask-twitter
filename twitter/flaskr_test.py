#!/usr/bin/env python
# encoding: utf-8
"""
flaskr_blog.py

Created by Delai on 2011-11-09.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
import os
import __init__ as flaskr
import unittest
import tempfile
import date_util
from flask import Markup, Flask, request



from flask import template_rendered
from contextlib import contextmanager

INDEX_URL= 'http://localhost:5000'

class flaskr_test(unittest.TestCase):
    def setUp(self):
        self.db_fp, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fp)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No entries here so far' in rv.data

    def test_login(self):
        rv = self.app.get('/login')
        assert '<form action="/login_valide"' in rv.data

    def login_valide(self, username, password):
        return self.app.post("/login_valide", data=dict(username=username, password=password), follow_redirects = True)
    
    def logout(self):
        return self.app.get("/logout", follow_redirects = True)
        
    def test_login_valide_and_logout(self):
        rv = self.login_valide('shidelai', 'shizai')
        assert 'You has log in successfully' in rv.data

        rv = self.logout()
        assert 'You were logged out' in rv.data
        assert 200 == rv.status_code
  
        rv = self.logout()
        assert 'You have not login right now' in rv.data

        rv = self.login_valide('notuser', 'the pas')
        assert 'No User Named' in rv.data
        rv = self.login_valide('shidelai', 'ddddd')
        assert 'Invalid Password' in rv.data
        

    def test_add_entry(self):
        username = 'shidelai'
        self.login_valide(username, 'shizai')
        rv = self.app.post('/add_entry', data=dict(author=username, title='<Hello>', text='<strong>HTML</strong> allowed here', redirect_url=INDEX_URL), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert 'New entry is successfully added' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data
        
    def test_user(self):
        app1 = Flask(__name__)
        with app1.test_request_context('/shidelai?age=12'):
            assert request.path == '/shidelai'
            assert request.url == 'http://localhost/shidelai?age=12'
            assert request.base_url == 'http://localhost/shidelai'
            assert request.url_root == 'http://localhost/'      #the full url root (with hostname), this is the application root
            assert request.host_url == 'http://localhost/'   #just the host with scheme
            assert request.query_string == 'age=12'

    def test_redirect(self):
        ctx = flaskr.app.test_request_context('/?next=%s/shidelai' % INDEX_URL)
        ctx.push()
        flaskr.app.preprocess_request()
        flaskr.app.process_response(flaskr.app.response_class())  # to shutdown a request
        assert flaskr.redirect_url() == "http://localhost:5000/shidelai"
        ctx.pop()
        
    
if __name__ == '__main__':
    unittest.main()
