'''
SQLAlchemy
'''
from database import db_session
from models import User
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
    u = User(request.form.get('username'), request.form.get('password'), request.form.get('email'))
    #db_session.delete(User.query.filter_by(name = "shidelai").first())
    User.query.filter(User.name == request.form.get('username')).delete()
    db_session.commit()
    flash('%sremoved' % request.form.get('username'), 'message')
    redirect(redirect_url())

@app.route("/show_user.html")
def show_user():
    return repr(User.query.filter_by(name = 'shidelai').first())

@app.route("/")
@templated('index.html')
def index():
    cur = db_conn().execute('select author, title, text, post_time from entries order by id desc')
    entries = [dict(author = row[0], title=row[1], text=row[2], time = date_util.str_from_timestamp(row[3])) for row in cur.fetchall()]
    return {'entries' : entries}

@app.route("/register.html")
@templated()
def register():
    pass


@app.route('/add_entry', methods = ['Post'])
@login_required
def add_entry():
    '''
    add entry action
    '''
    db_conn().execute('insert into entries (author, title, text, post_time) values (?, ?, ?, ?)', [request.form['author'], request.form['title'], text_util.html_process(request.form['text']), date_util.now_timestamp()])
    db_conn().commit()
    flash('New entry is successfully added')
    return redirect(redirect_url())

@app.route("/<request_username>")
def user(request_username):
    app.logger.debug("user(request_username) CALLED")
    if users.is_user(request_username):
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

@app.route("/login.html")
@templated()
def login():
    if 'username' in session:
        flash("You logged in already!", "message")
        return redirect(url_for('index'))
    return {"next": request.referrer}

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
        approved, message = users.user_valide(request.form['username'], request.form['password'])
        if approved:
            session['username'] = request.form['username']
            flash("You has log in successfully", "message")
            app.logger.debug(request.form['username'] + ' approved, redirect to index page')
            return redirect(redirect_url())
        else:
            pw_error_signal.send(app, msg = 'password Error', username = request.form['username'])    #app is sender, paras can be more than two
            flash(message, "error")
            app.logger.debug(request.form['username'] + ' not approved, redirect to index page'  + ' message : ' + str(message))
            return redirect(url_for('login'))
    else:
        return "Other Methods"

@app.errorhandler(404)
def error_404(error):
    app.logger.error('404 error')
    return render_template("404.html", error=error), 404

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