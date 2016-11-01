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

"""
    ~~~~~~~~~
    Views.py
    ~~~~~~~~~    
"""

def login_required(f):
    ''' 주요 기능 사용과 관련하여 로그인 체크를 진행하는 함수.

        login check가 필요한 부분에
        @login_required를 입력하여 사용

    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session:
            pass
        else:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    ''' file extention 필터링 함수

        (now) only .zip allowed
    '''

    ALLOWED_EXTENSIONS = set(['zip'])

    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    '''
        서비스 접속 시 세션 상태에 맞게 리다이렉트가 시작되는 페이지
    '''
    if 'email' not in session or 'auth' not in session:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
        로그인 페이지
    '''
    error = None
    # new_u = People('3ncag3', '3ncag3@gmail.com', '1111', True);
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
            session.permanent = True
            return redirect(url_for('dashboard'))
        return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    '''
        프로젝트 선택 화면
        

        :modal_type insert: 프로젝트 생성

        :modal_type info: 프로젝트 정보

        :modal_type connect: 프로젝트 선택

        :modal_type delete: 프로젝트 삭제

    '''
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

        elif modal_type == "clone":
            
            projName = request.form.get('projName')
            projDesc = request.form.get('projDesc')
            project_name = request.form.get('project_name')
            origin_project = Project.query.filter(Project.projName==project_name).first()
            new_project = Project(projName, projDesc, user_data.pID, origin_project.fileNum)
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

    '''
        프로젝트 정보
    '''
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


origin_file = ""
comp_file = ""

@app.route('/file_upload', methods=['GET', 'POST'])
@login_required
def file_upload():

    '''
        파일 업로드


        upload file path

        :원본 파일: server/uploads/<projName>/origin/<filename>
        :비교 파일: server/uploads/<projName>/compare/<filename>

    '''
    
    projName = ""

    global origin_file
    global comp_file
    

    if not session['project'] or session['project'] == "":
        return redirect(url_for('dashboard'))
    else:
        projName = session['project']

        if request.method == 'POST':

            post_type = request.form.get('post_type')

            if not post_type:

                file = request.files['file']

                if file and allowed_file(file.filename):

                    filename = secure_filename(file.filename)

                    file_type = request.form.get('file_type')

                    if file_type == "origin_file":
                        if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'origin')):
                            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'origin'))

                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'origin', filename))
                        origin_file = os.path.join(app.config['UPLOAD_FOLDER'], projName, 'origin', filename)

                        print (origin_file, file=sys.stderr)
                        
                    elif file_type == "compare_file":

                        if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'compare')):
                            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'compare'))
                        
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'compare', filename))
                        # comp_file = zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'compare', filename))
                        comp_file = os.path.join(app.config['UPLOAD_FOLDER'], projName, 'compare', filename)
                        print (comp_file, file=sys.stderr)

                    else:
                        print ("upload type error", file=sys.stderr)

                else:
                    print ("only zip file", file=sys.stderr)

            elif post_type == 'file_upload':

                if not origin_file or not comp_file:
                    # file miss
                    print (origin_file, file=sys.stderr)
                    print (comp_file, file=sys.stderr)
                    print ("no file", file=sys.stderr)
                    pass
                else:
                    
                    file_data = File(origin_file, comp_file)
                    db.session.add(file_data)
                    db.session.commit()

                    file_data = File.query.filter(File.originPath==origin_file).first()

                    project_data = Project.query.filter(Project.projName==projName).first()
                    project_data.fileNum = file_data.fileID
                    db.session.commit()

                    return redirect(url_for('tuple'))

            else:
                pass

        else:
            pass

    return render_template('/file_upload.html', projName=projName, origin_file=origin_file, comp_file=comp_file)


@app.route('/tuple', methods=['GET', 'POST'])
@login_required
def tuple():

    '''
        비교쌍 생성
    '''

    projName = ""

    if not session['project'] or session['project'] == "":
        return redirect(url_for('dashboard'))
    else:
        projName = session['project']
        project_data = Project.query.filter(Project.projName==projName).first()
        file_data = File.query.filter(File.fileID==project_data.fileNum).first()

        origin_file = zipfile.ZipFile(file_data.originPath)
        comp_file = zipfile.ZipFile(file_data.compPath)

        origin_list = []
        comp_list = []

        # file_list.extractall(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'origin'))
        # file_list.extractall(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'compare'))

        for ori in origin_file.namelist():
            origin_list.append(ori)
            print (ori, file=sys.stderr)

        for comp in comp_file.namelist():
            comp_list.append(comp)
            print (comp, file=sys.stderr)


        # 같은 이름 파일

        # 모든 파일 one by one

        # 사용자가 지정

    return render_template('/tuple.html', projName=projName)


@app.route('/logout', methods=['GET',   'POST'])
@login_required
def logout():
    '''
        로그아웃 및 세션 초기화
    '''
    session.clear()
    return redirect(url_for('login'))