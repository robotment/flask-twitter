# coding=utf-8

from contextlib import closing

import sqlite3
from flask import Flask, request, render_template, make_response, session, redirect, url_for, flash, g, abort, Markup
import logging

import user_center, date_util, text_util

from flask import template_rendered
from blinker import Namespace

from flask.views import View



app = Flask(__name__)


app.config.from_pyfile('config.py', silent = False)

text_util.INDEX_URL = app.config['INDEX_URL']


###
# blueprint
#
from pages import simple_page
app.register_blueprint(simple_page, url_prefix='/pages')


###
# blinker singal
# 
def pw_error_record(sender, **data):
    app.logger.info('receive SIGNAL from %s, data: %s' % (sender, data))
blinker_ns = Namespace()
pw_error_signal = blinker_ns.signal('error_signal')
pw_error_signal.connect(pw_error_record, app)  # only receive the signal send from app, equals to .connect(pw_error_record, sender = app)

@template_rendered.connect_via(app)
def when_template_rendered(sender, template, context):
    #print 'Template %s is rendered with %s' % (template.name, context)
    #app.logger.debug('Template %s is rendered' % (template.name))
    #print 'sender: %s' % (sender)
    pass
###



'''
DB
'''
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def db_conn():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = connect_db()
    return db


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


                
@app.before_request
def before_request():
    app.logger.debug('before_request() called')
    

# @app.after_request
# def after_request(abc):
#   app.logger.debug('after_request() called')
 
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        db_conn().close()        

###
# redirct_url
#
def redirect_url():
    #app.logger.debug('request.args.get(\'next\') = %s, request.form[\'next\'] = %s, referrer = %s' \
    #                 % (request.args.get('next'), request.form.get('next'), request.referrer))
    next = request.args.get('next') or \
           request.form.get('next') or \
           request.referrer or \
           url_for('index')
    app.logger.debug('Redirect to %s' % next)
    
    return next
###

'''
mail extends
'''

from flaskext.mail import Mail, Message
mail = Mail(app)
@app.route("/mail")
def send_mail():
    from datetime import datetime
    msg = Message("Hello",
                  sender = ("Delai.me", "me@delai.me"),
                  recipients=["to.too@qq.com", 'shidelai@gmail.com'])
    #msg.body = "testing"
    msg.html = "<h1>testing</h1> <p>%s</p> " % datetime.now()
    mail.send(msg)
    return 'email sended'


@app.url_defaults
def check_language_code(endpoint, values):
    '''
    app.url_defaults decorator add the fuction below to 
    url_default_functions : A dictionary with a lists of functions 
    CALLED while url_for is called, so will be called many time in one http request 
    '''

    app.logger.debug('endpoint: %s, values: %s' % (endpoint, repr(values)))

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

    app.logger.debug('app.url_value_preprocessor > lang_code_process called')
    if 'lang_code' in request.args:
        g.lang_code = request.args['lang_code']
        app.logger.info('change language setting to %s' % g.lang_code)
    
    # if values and 'lang_code' in values:
    #     app.logger.debug('values[lang_cod]: %s' % values['lang_code'])
    #     g.lang_code = values.pop('lang_code', None)
    # else:
    #     app.logger.debug('no lang_code in values')


'''
SQLAlchemy
'''
from twitter.database import db_session
from twitter.models import User
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/add_user", methods = ['Post'])
def add_user():
    u = User(request.form.get('username'), request.form.get('password'), request.form.get('email'))
    app.logger.debug("add_user() Called")
    if User.query.filter(User.name == u.name).first():
        app.logger.debug("User existed")
        flash("User exist", "error")
    elif User.query.filter(User.email == u.email).first():
        app.logger.debug("Email existed")
        flash("Email exist", "error")
    else:
        db_session.add(u)
        db_session.commit()
        flash("Register Successfull for <a href=\"/%s\">@%s</a>" % (u.name, u.name), "message")
        session['username'] = u.name
        return redirect(url_for('index'))
    return redirect(redirect_url())
    
@app.route("/remove_user")
def remove_user():
    u = User('shidelai', 'shidelai', 'shidelai@gmail.com')
    db_session.delete(User.query.filter_by(name = "shidelai").first())
    db_session.commit()
    return 'shidelai removed'
    
@app.route("/show_user")
def show_user():
    return repr(User.query.filter_by(name = 'shidelai').first())

@app.route("/")
def index():
    cur = db_conn().execute('select author, title, text, post_time from entries order by id desc')
    entries = [dict(author = row[0], title=row[1], text=row[2], time = date_util.str_from_timestamp(row[3])) for row in cur.fetchall()]
    return render_template("index.html", entries = entries)

@app.route("/register")
def register():
    return render_template("register.html")

def login_check(f):
    def decorator():    
        if not session.get('username'):
            return redirect(url_for('login'))
        else:
            '''
            not f() here, otherwise, equal to "redirect(redirect_url())" in this line, 
            but not "return redirect(redirect_url())", which is supposed to be
            '''
            return f()        
    return decorator

@app.route('/add_entry', methods = ['Post'])
@login_check
def add_entry():
    #app.logger.debug("already login, start insert execute sql")
    db_conn().execute('insert into entries (author, title, text, post_time) values (?, ?, ?, ?)', [request.form['author'], request.form['title'], text_util.html_process(request.form['text']), date_util.now_timestamp()])
    db_conn().commit()
    flash('New entry is successfully added')
    return redirect(redirect_url())

@app.route("/markup")
def markup():
    str = ('<strong>Hello %s!</strong>') % '<blink>hacker</blink>'
    return render_template("markup.html", str=str)


@app.route("/<request_username>")
def user(request_username):
    app.logger.debug("user(request_username) CALLED")
    if user_center.is_user(request_username):
        app.logger.debug(request_username + " is registed user")
        cur = db_conn().execute('select author, title, text, post_time from entries where author = ? order by id desc', [request_username])
        entries = [dict(author = row[0], title=row[1], text=row[2], time = date_util.str_from_timestamp(row[3])) for row in cur.fetchall()]
        if(request_username == session.get('username')):
            #app.logger.debug(username + ' visit his home page')
            return render_template("user_addform.html", request_username=request_username, entries = entries)
        else:
            #app.logger.debug('You are visit' + username + ' \'s home page')
            return render_template("user.html", request_username=request_username, entries = entries)
    else:
        app.logger.info("%s is not registed user abort 404" % request_username)   
        abort(404)

@app.route("/post/<post_id>")
def post(post_id):
    return "post %s"%(post_id)

@app.route("/search")
def search():
    if request.method == 'GET':
        query = request.args.get('q', '')
    return query

@app.route("/login")
def login():
    if 'username' in session:
        flash("You logged in already!", "message")
        return redirect(url_for('index'))
    return render_template("login.html", next = request.referrer)

@app.route("/logout")
def logout():
    if 'username' in session:
        app.logger.debug('pop out username: %s' % session.get('username'))
        session.pop('username', None) 
        flash('You were logged out', 'message')
    else:
        flash('You have not login right now', 'message')    
    return redirect(redirect_url())

@app.route("/login_valide", methods=['GET', 'POST'])
def login_valide():
    message = None
    if request.method == 'POST':
        approved, message = user_center.user_valide(request.form['username'], request.form['password'])
        if approved:
            session['username'] = request.form['username']
            flash("You has log in successfully", "message")
            app.logger.debug(request.form['username'] + ' approved, redirect to index page')
            return redirect(redirect_url())
        else:
            pw_error_signal.send(app, msg = 'password Error', username = request.form['username'])    #app is sender, paras can be more than two
            flash(message, "error")
            app.logger.debug(request.form['username'] + ' not approved, redirect to index page'  + ' message : ' + str(message))
            return redirect(redirect_url())
    else:
        return "Other Methods"

@app.errorhandler(404)
def error_404(error):
    app.logger.error('404 error')
    return render_template("404.html", error=error), 404


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
#         return self.get_entries()
# 
#     def get_entries(self):
#         return [dict(author = row[0], title=row[1], text=row[2], time = date_util.str_from_timestamp(row[3])) for row in self.cur.fetchall()]
# 
# class AllEntriesView(EntriesView):
#     cur = db_conn().execute('select author, title, text, post_time from entries order by id desc')
# 
# class UserEntriesView(EntriesView):
#     cur = db_conn().execute('select author, title, text, post_time from entries where author = "%s" order by id desc' % (username))
# 
# app.add_url_rule('/', view_func=AllEntriesView.as_view('index.html'))
# 
# ###



if __name__ == "__main__":
  
    app.run()
