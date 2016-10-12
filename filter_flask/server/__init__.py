import os
import random
import string
from flask import Flask
from flask import session
from flask_sqlalchemy import SQLAlchemy
from server.module.redis_session import RedisSessionInterface

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20))
    return session['_csrf_token']

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///tmp/soan.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.jinja_env.globals['csrf_token'] = generate_csrf_token

# Flask REDIS Session Interface SETTINGS
app.session_interface = RedisSessionInterface()
app.config.update(SESSION_COOKIE_NAME = 'server_session')

db = SQLAlchemy(app, session_options={"autoflush": False})

import server.views