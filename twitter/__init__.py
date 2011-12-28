# coding=utf-8

from contextlib import closing

import sqlite3
from flask import Flask, request, render_template, make_response, session, redirect, url_for, flash, g, abort, Markup
import logging

import users, date_util, text_util

from flask import template_rendered
from blinker import Namespace

app = Flask(__name__)
app.config.from_pyfile('config.py', silent = False)
text_util.INDEX_URL = app.config['INDEX_URL']

'''
    blueprint
'''
from pages import simple_page
app.register_blueprint(simple_page, url_prefix='/pages')

'''
    blinker singal
'''
def pw_error_record(sender, **data):
    app.logger.info('receive SIGNAL from %s, data: %s' % (sender, data))

blinker_ns = Namespace()
pw_error_signal = blinker_ns.signal('error_signal')
pw_error_signal.connect(pw_error_record, app)  # only receive the signal send from app, equals to .connect(pw_error_record, sender = app)

@template_rendered.connect_via(app)
def when_template_rendered(sender, template, context):
    '''
        template_rendered is the sender
    '''
    pass

'''
    redirct_url
'''
def redirect_url():
    #app.logger.debug('request.args.get(\'next\') = %s, request.form[\'next\'] = %s, referrer = %s' \
    #                 % (request.args.get('next'), request.form.get('next'), request.referrer))
    next = request.args.get('next') or \
           request.form.get('next') or \
           request.referrer or \
           url_for('index')
    app.logger.debug('Redirect to %s' % next)
    
    return next

'''
    hack location
'''
@app.before_request
def before_request():
    app.logger.debug('before_request() called')
 
@app.teardown_request
def teardown_request(exception):
    pass      


@app.url_defaults
def check_language_code(endpoint, values):
    '''
    app.url_defaults decorator add the fuction below to 
    url_default_functions : A dictionary with a lists of functions 
    CALLED while url_for is called, so will be called many time in one http request 
    '''

    #app.logger.debug('endpoint: %s, values: %s' % (endpoint, repr(values)))

    # 
    #     if hasattr( g, 'lang_code'):
    #         app.logger.debug("lang_code: %s" % g.lang_code)
    #     else:
    #         app.logger.debug('no lang_code')
    #     return


    # if app.url_map.is_endpoint_expecting(endpoint, 'lang_code'):
    #        app.logger.debug('values[lang_code] = g.lang_code')
    #        values['lang_code'] = g.lang_code


@app.url_value_preprocessor
def lang_code_process(endpoint, values):
    '''
    CALLED while process http request. ( called before url_default_functions like check_language_code()) 
    '''
    # 
    # if 'lang_code' in request.args:
    #     g.lang_code = request.args['lang_code']
    #     app.logger.info('change language setting to %s' % g.lang_code)

    # if values and 'lang_code' in values:
    #     app.logger.debug('values[lang_cod]: %s' % values['lang_code'])
    #     g.lang_code = values.pop('lang_code', None)
    # else:
    #     app.logger.debug('no lang_code in values')


from views import *


# ###
# # pluggable views
# #
# class ListView(View):
# 
#     username = None
#     template_name = None
# 
#     def __init__(self, template_name):
#         self.template_name = template_name
# 
#     def render_template(self, context):
#         return render_template(self.template_name, **context)
# 
#     def dispatch_request(self):
#         context = {'username': self.username,
#                    'objects': self.get_objects()
#                    }
#         return self.render_template(context)
# 
# class EntriesView(ListView):
# 
#     if 'username' in session:
#         username = session['username']
# 
#     cur = None
# 
#     def get_objects():
#         return self.get_tweets()
# 
#     def get_tweets(self):
#         return [dict(author = row[0], title=row[1], text=row[2], time = date_util.str_from_timestamp(row[3])) for row in self.cur.fetchall()]
# 
# class AllEntriesView(EntriesView):
#     cur = db_conn().execute('select author, title, text, post_time from tweets order by id desc')
# 
# class UserEntriesView(EntriesView):
#     cur = db_conn().execute('select author, title, text, post_time from tweets where author = "%s" order by id desc' % (username))
# 
# app.add_url_rule('/', view_func=AllEntriesView.as_view('index.html'))
# 
# ###



if __name__ == "__main__":
  
    app.run()
