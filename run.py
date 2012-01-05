from twxt import app
from datetime import datetime

print " * %s" % datetime.now()

import flask



if app.debug:
    '''
    if not app.debug in product mode
    '''

    import logging


    '''
    when flask app was init, there is only one default debug level handler bind to the logger
    '''
    app.logger.handlers[0].setLevel(logging.INFO)

    '''
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1', 'server-error@delai.me', app.config['ADMINS_EMAIL'], 'YourApplication Failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
    '''

    from logging import FileHandler
    file_handler = FileHandler('log')
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

app.run()
