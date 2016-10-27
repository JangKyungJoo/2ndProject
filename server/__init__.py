import os
import random
import string

from flask import Flask
from flask import session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta


'''
	source analysis (soan)

	:copyright: (c) 2016 by software maestro
	:license: soan

'''

__version__ = '1.0'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///tmp/soan.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.permanent_session_lifetime = timedelta(minutes=10)

# Flask REDIS Session Interface SETTINGS
# app.session_interface = RedisSessionInterface()
app.config.update(SESSION_COOKIE_NAME = 'server_session')

db = SQLAlchemy(app, session_options={"autoflush": False})

import server.views
import server.result
import server.filter