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
import zipfile


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


@app.route('/dashboard', methods=['GET', 'POST'])
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
            projDesc = request.form.get('projDesc')
            new_project = Project(projName, projDesc, user_data.pID)
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

    return render_template('/dashboard.html', user_data=user_data, project_list=project_list)


@app.route('/proj_info', methods=['GET', 'POST'])
@login_required
def proj_info():

    projName = ""

    if not session['project'] or session['project'] == "":
        return redirect(url_for('dashboard'))
    else:
        projName = session['project']
        project = Project.query.filter(Project.projName==projName).first()
        user = People.query.filter(People.pID==project.pID).first()
        user_name = user.pName
        projDesc = project.projDesc
        fileNum = project.fileNum
        if fileNum is None:
            file_desc = "no file"
        else:
            file_desc = fileNum

        date = project.date
        update_time = project.update


    return render_template('/proj_info.html',
        projName=projName, projDesc=projDesc, 
        fileNum=fileNum, date=date, file_desc=file_desc,
        user_name=user_name, update_time=update_time)


@app.route('/file_upload', methods=['GET', 'POST'])
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

                file_type = request.form.get('file_type')
                
                if file_type == "origin_file":
                    file_list = zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    print (file_list.namelist(), file=sys.stderr)
                    file_list.extractall(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'origin'))
                elif file_type == "compare_file":
                    file_list = zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], 'filename'))
                    print (file_list.namelist(), file=sys.stderr)
                    file_list.extractall(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'compare'))
                else:
                    print ("upload type error", file=sys.stderr)
            else:
                print ("only zip file", file=sys.stderr)

    return render_template('/file_upload.html', projName=projName)


@app.route('/tuple', methods=['GET', 'POST'])
@login_required
def tuple():

    projName = ""

    if not session['project'] or session['project'] == "":
        return redirect(url_for('dashboard'))
    else:
        projName = session['project']
        origin_file_list = list()
        compare_file_list = list()


        
    return render_template('/tuple.html', projName=projName)


@app.route('/logout', methods=['GET',   'POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))