#-*- coding: utf-8 -*-
from __future__ import print_function
from server.models import * 
from server import app
from server import db
from server.models import People
from server.models import Project
from server.models import File
from server.models import Result
from functools import wraps
from flask import render_template
from flask import send_from_directory
from flask import request, redirect, url_for
from flask import session
from flask import make_response
from flask import abort
from flask import flash
from flask import Markup
from flask import jsonify
from werkzeug import secure_filename
from datetime import date, timedelta
import os
import base64
import sys
import json
import requests


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session:
            pass
        else:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['zip'])

    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    if 'email' not in session or 'auth' not in session:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    # new_u = People('3ncag3', '3ncag3@gmail.com', 'Djfrdjfg1!', True);
    # db.session.add(new_u)
    # db.session.commit()
    
    if 'email' in session and 'auth' in session:
        if session['auth'] == "true":
            return redirect(url_for('dashboard'))
    if request.method=='GET':
        return render_template('login.html')
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = People.query.filter(People.pEmail==username).first()

        if not user or not user.verify_password(password):
            error = "암호가 틀렸거나 없는 계정입니다"
            return render_template('login.html', error=error)
        else:
            session['email'] = user.pEmail
            session['is_admin'] = user.pAuth
            session['auth'] = "true"
            return redirect(url_for('dashboard'))
        return render_template('login.html')


@app.route('/board/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not session or 'auth' not in session:
        session.clear()
        return redirect(url_for('login'))
    elif session['auth'] == "false":
        session.clear()
        return redirect(url_for('login'))
    else:
        user_data = People.query.filter(People.pEmail==session['email']).first()
        project_list = Project.query.filter(Project.pID==user_data.pID).all()
        session['project'] = ""

    if request.method=='POST':
        modal_type = request.form.get('modal_type')
        if not modal_type:
            pass
        elif modal_type == "insert":

            projName = request.form.get('projName')
            new_project = Project(projName, user_data.pID)
            db.session.add(new_project)
            db.session.commit()

            return redirect(url_for('dashboard'))

        elif modal_type == "info":

            projName = request.form.get('projName')
            session['project'] = projName
            return redirect(url_for('proj_info'))

        elif modal_type == "connect":

            projName = request.form.get('projName')
            session['project'] = projName
            return redirect(url_for('file_upload'))

        elif modal_type == "delete":

            password = request.form.get('password')
            if not user_data.verify_password(password):
                pass
            else:
                projName = request.form.get('projName')
                proj = Project.query.filter(Project.projName==projName).filter(Project.pID==user_data.pID).first()
                db.session.delete(proj)
                db.session.commit()

                return redirect(url_for('dashboard'))   

    return render_template('/board/dashboard.html', user_data=user_data, project_list=project_list)


@app.route('/board/proj_info', methods=['GET', 'POST'])
@login_required
def proj_info():

    projName = ""

    if not session['project'] or session['project'] == "":
        return redirect(url_for('dashboard'))
    else:
        projName = session['project']
        project = Project.query.filter(Project.projName==projName).first()


    return render_template('/board/proj_info.html')


@app.route('/board/file_upload', methods=['GET', 'POST'])
@login_required
def file_upload():

    projName = ""

    if not session['project'] or session['project'] == "":
        return redirect(url_for('dashboard'))
    else:
        projName = session['project']
        
        if request.method == 'POST':

            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                print ("only zip file", file=sys.stderr)

    return render_template('/board/file_upload.html', projName=projName)


@app.route('/board/tuple', methods=['GET', 'POST'])
@login_required
def tuple():

    projName = ""

    if not session['project'] or session['project'] == "":
        return redirect(url_for('dashboard'))
    else:
        projName = session['project']
        origin_file_list = list()
        comp_file_list = list()
        
    return render_template('/board/tuple.html', projName=projName)


@app.route('/logout', methods=['GET',   'POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))