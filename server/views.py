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
from flask import request
from flask import redirect
from flask import url_for
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

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


@app.route('/')
def index():
    if 'email' not in session or 'auth' not in session:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
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
def dashboard():
    if not session or 'auth' not in session:
        session.clear()
        return redirect(url_for('login'))
    elif session['auth'] == "false":
        session.clear()
        return redirect(url_for('login'))
    else:
        user_data = People.query.filter(People.pEmail==session['email']).first()
        project_list = Project.query.filter(Project.pNum==user_data.pNum).all()

    if request.method=='POST':
        modal_type = request.form.get('modal_type')
        if not modal_type:
            pass
        elif modal_type == "insert":

            projName = request.form.get('projName')
            new_project = Project(projName, user_data.pNum)
            db.session.add(new_project)
            db.session.commit()

            return redirect(url_for('dashboard'))

        elif modal_type == "connect":
            
            pass
        elif modal_type == "delete":

            password = request.form.get('password')
            if not user_data.verify_password(password):
                pass
            else:
                projName = request.form.get('projName')
                proj = Project.query.filter(Project.projName==projName).filter(Project.pNum==user_data.pNum).first()
                db.session.delete(proj)
                db.session.commit()

                return redirect(url_for('dashboard'))   

    return render_template('/board/dashboard.html', user_data=user_data, project_list=project_list)


@app.route('/board/tuple', methods=['GET', 'POST'])
def tuple():
    if request.method == 'GET':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':

        for origin_file in origin_folder:
            pass
        for comp_file in comp_folder:
            pass

        file_dict = dict()

        # ???

    return render_template('/board/tuple.html')


@app.route('/logout', methods=['GET',   'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))