#-*- coding: utf-8 -*-
from __future__ import print_function

import shutil

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
from flask import send_file
from werkzeug import secure_filename
from datetime import date, timedelta
from os import walk
from os.path import isfile, join
import os
import base64
import sys
import json
import requests
import zipfile
import csv

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
    admin_u = People('admin', 'admin@admin.com', '1111', True);
    if not People.query.filter(People.pName==admin_u.pName).first():
        db.session.add(admin_u)    
    db.session.commit()

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
        테스트용 코드 by Sang-jin Moon
        db.session.query(Pair).delete()
        db.session.query(Origin).delete()
        db.session.query(Compare).delete()
        db.session.query(Result).delete()
        db.session.commit()
    '''

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
        session['projID'] = None

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
            projID = request.form.get('projID')
            session['projID'] = projID
            session['project'] = projName
            return redirect(url_for('proj_info'))

        elif modal_type == "connect":

            projName = request.form.get('projName')
            projID = request.form.get('projID')
            session['projID'] = projID
            session['project'] = projName

            project = Project.query.get(projID)
            if project.fileNum is None:
                return redirect(url_for('file_upload'))
            else:
                return redirect(url_for('tuple'))

        elif modal_type == "delete":

            password = request.form.get('password')
            if not user_data.verify_password(password):
                pass
            else:
                projID = request.form.get('projID')
                project = Project.query.get(projID)
                pair = Pair.query.filter(Pair.projID == projID).all()
                for item in pair:
                    result = Result.query.filter(Result.pairID == item.pairID).all()
                    for temp in result:
                        db.session.delete(temp)
                    db.session.delete(item)

                origin = Origin.query.filter(Origin.projID == projID).all()
                for item in origin:
                    db.session.delete(item)

                compare = Compare.query.filter(Compare.projID == projID).all()
                for item in compare:
                    db.session.delete(item)

                file = File.query.get(project.fileNum)
                if file:
                    db.session.delete(file)
                    
                db.session.delete(project)

                db.session.commit()

                path = join(app.config['UPLOAD_FOLDER'], projID)
                if os.path.exists(path):
                    shutil.rmtree(path)

                return redirect(url_for('dashboard'))   

    return render_template('/dashboard.html', user_data=user_data, project_list=project_list)


@app.route('/proj_info', methods=['GET', 'POST'])
@login_required
def proj_info():

    '''
        프로젝트 정보
    '''
    if not session['projID'] or session['projID'] is None:
        return redirect(url_for('dashboard'))
    else:
        project = Project.query.get(session['projID'])
        projName = project.projName
        user = People.query.filter(People.pID==project.pID).first()
        user_name = user.pName
        projDesc = project.projDesc
        fileNum = project.fileNum
        file = File.query.filter(File.fileID==fileNum).first()
        if fileNum is None:
            file_desc = "no file"
        else:
            file_desc = file.originPath + " , " + file.compPath

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

    global origin_file
    global comp_file
    

    if not session['projID'] or session['projID'] is None:
        return redirect(url_for('dashboard'))
    else:
        projID = session['projID']
        project = Project.query.get(projID)
        projName = project.projName

        if request.method == 'POST':

            post_type = request.form.get('post_type')

            if not post_type:

                file = request.files['file']

                if file and allowed_file(file.filename):

                    filename = secure_filename(file.filename)

                    file_type = request.form.get('file_type')

                    if file_type == "origin_file":
                        if not os.path.exists(join(app.config['UPLOAD_FOLDER'], projID, 'origin')):
                            os.makedirs(join(app.config['UPLOAD_FOLDER'], projID, 'origin'))

                        file.save(join(app.config['UPLOAD_FOLDER'], projID, 'origin', filename))
                        origin_file = join(app.config['UPLOAD_FOLDER'], projID, 'origin', filename)

                    elif file_type == "compare_file":

                        if not os.path.exists(join(app.config['UPLOAD_FOLDER'], projID, 'compare')):
                            os.makedirs(join(app.config['UPLOAD_FOLDER'], projID, 'compare'))
                        
                        file.save(join(app.config['UPLOAD_FOLDER'], projID, 'compare', filename))
                        # comp_file = zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], projName, 'compare', filename))
                        comp_file = join(app.config['UPLOAD_FOLDER'], projID, 'compare', filename)

                    else:
                        print ("upload type error", file=sys.stderr)

                else:
                    print ("only zip file", file=sys.stderr)

            elif post_type == 'file_upload':

                if not origin_file or not comp_file:
                    # file miss
                    print ("no file", file=sys.stderr)
                    pass
                else:

                    origin_file = zipfile.ZipFile(origin_file)
                    comp_file = zipfile.ZipFile(comp_file) 

                    origin_file.extractall(join(app.config['UPLOAD_FOLDER'], projID, 'origin', 'files'))
                    comp_file.extractall(join(app.config['UPLOAD_FOLDER'], projID, 'compare', 'files'))

                    origin_path = join(app.config['UPLOAD_FOLDER'], projID, 'origin', 'files')
                    comp_path = join(app.config['UPLOAD_FOLDER'], projID, 'compare', 'files')
                    
                    file_data = File(origin_path, comp_path)
                    
                    if not File.query.filter(File.originPath==origin_path).filter(File.compPath==comp_path).first():
                        db.session.add(file_data)

                    db.session.commit()

                    file_data = File.query.filter(File.originPath==origin_path).first()
                    project.fileNum = file_data.fileID

                    db.session.commit()

                    return redirect(url_for('tuple'))

            else:
                pass

        else:
            pass

    return render_template('/file_upload.html', projName=projName, origin_file=origin_file, comp_file=comp_file)


g_tuple_list = {}
ext_list = []

@app.route('/tuple', methods=['GET', 'POST'])
@login_required
def tuple():

    '''
        비교쌍 생성

        1. zip 파일 내 모든 파일의 확장자 수집 및 카운트
        2. 확장자 별 비교 기능 제공
        3. 같은 이름의 파일 비교, 같은 확장자만 비교, 전체 파일 비교 기능
    '''

    global ext_list

    if not session['projID'] or session['projID'] is None:
        return redirect(url_for('dashboard'))
    else:

        tuple_list = []

        projID = session['projID']
        project = Project.query.get(projID)
        projName = project.projName
        file_data = File.query.filter(File.fileID==project.fileNum).first()

        if file_data is None:
            return redirect(url_for('file_upload'))

        origin_path = file_data.originPath
        comp_path = file_data.compPath

        origin_file_list = []
        comp_file_list = []
        origin_list = []
        comp_list = []
        ext_list = [] # file extension list

        for path, subdirs, files in walk(origin_path):
            for name in files:
                temp_ext = name.rsplit('.', 1)
                if len(temp_ext) > 1:
                    ext = temp_ext[1]

                    if ext not in ext_list:
                        ext_list.append(ext)

                origin_file_list.append(name)
                origin_list.append(join(path,name))
                original = open(join(path,name))
                original_lineNum = 0
                for line in original.readlines():
                    if len(line) > 2:
                        original_lineNum+=1
                #original_lineNum = len(original.readlines())
                origin_file = Origin(name, path, original_lineNum, projID)

                if not Origin.query.filter(Origin.originName==name).filter(Origin.originPath==path).filter(Origin.lineNum==original_lineNum).filter(Origin.projID==projID).first():
                    db.session.add(origin_file)

        for path, subdirs, files in walk(comp_path):
            for name in files:
                temp_ext = name.rsplit('.', 1)
                if len(temp_ext) > 1:
                    ext = temp_ext[1]
                    if ext not in ext_list:
                        ext_list.append(ext)

                comp_file_list.append(name)
                comp_list.append(join(path,name))
                compare = open(join(path,name))
                compare_lineNum = 0
                for line in compare.readlines():
                    if len(line) > 2:
                        compare_lineNum += 1
                #compare_lineNum = len(compare.readlines())
                comp_file = Compare(name, path, compare_lineNum, projID)

                if not Compare.query.filter(Compare.compName==name).filter(Compare.compPath==path).filter(Compare.lineNum==compare_lineNum).filter(Compare.projID==projID).first():
                    db.session.add(comp_file)

        db.session.commit()

    if request.method == 'POST':

        extension_list = []

        extension_list = request.form.getlist('extensions')

        temp_ori_list = []
        for ori in origin_list:
            if len(ori.rsplit('.', 1)) > 1:
                if ori.rsplit('.', 1)[1] in extension_list:
                    temp_ori_list.append(ori)
        origin_list = temp_ori_list

        temp_comp_list = []
        for comp in comp_list:
            if len(comp.rsplit('.', 1)) > 1:
                if comp.rsplit('.', 1)[1] in extension_list:
                    temp_comp_list.append(comp)
        comp_list = temp_comp_list

        tuple_type = request.form.get('tuple_type')

        # 같은 이름 파일
        if tuple_type == 'same':
            for ori in origin_list:
                for comp in comp_list:
                    if ori.rsplit('/', 1)[1] == comp.rsplit('/', 1)[1]:
                        tuple_list.append((ori.encode('ascii'), comp.encode('ascii')))
                    else:
                        continue

            g_tuple_list[projID] = tuple_list
            return render_template('/tuple_edit.html', tuple_list=tuple_list, projName=projName)
        # 모든 파일 one by one
        elif tuple_type == 'all':
            for ori in origin_list:
                for comp in comp_list:
                    tuple_list.append((ori.encode('ascii'), comp.encode('ascii')))
            g_tuple_list[projID] = tuple_list
            return render_template('/tuple_edit.html', tuple_list=tuple_list, projName=projName)
        # 같은 확장자끼리 비교
        elif tuple_type == 'ext':
            for ori in origin_list:
                for comp in comp_list:
                    if ori.rsplit('.', 1)[1] == comp.rsplit('.', 1)[1]:
                        tuple_list.append((ori.encode('ascii'), comp.encode('ascii')))
            g_tuple_list[projID] = tuple_list
            return render_template('/tuple_edit.html', tuple_list=tuple_list, projName=projName)
        else:
            pass

    return render_template('/tuple.html', projName=projName, origin_list=origin_list, comp_list=comp_list, 
        origin_file_list=origin_file_list, comp_file_list=comp_file_list, ext_list=ext_list)


@app.route('/tuple_edit', methods=['GET', 'POST'])
@login_required
def tuple_edit():

    '''
        비교쌍 편집

        - 생성된 비교쌍 확인 페이지
        - csv save, load로 비교쌍 편집 가능
    '''
    projID = session['projID']
    tuple_list = g_tuple_list.get(projID, list())

    if not session['projID'] or session['projID'] is None:
        return redirect(url_for('dashboard'))
    else:

        projID = session['projID']
        project_data = Project.query.get(projID)
        projName = project_data.projName

    if request.method == 'POST':

        for pair in tuple_list:
            origin_path = pair[0].rsplit('/',1)[0]
            origin_file = pair[0].rsplit('/',1)[1]

            comp_path = pair[1].rsplit('/',1)[0]
            comp_file = pair[1].rsplit('/',1)[1]

            originID = Origin.query.filter(Origin.originName==origin_file).filter(Origin.originPath==origin_path).filter(Origin.projID==projID).first().originID
            compID = Compare.query.filter(Compare.compName==comp_file).filter(Compare.compPath==comp_path).filter(Compare.projID==projID).first().compID

            new_pair = Pair(originID, compID, projID) # edit

            if not Pair.query.filter(Pair.originID==originID).filter(Pair.compID==compID).filter(Pair.projID==projID).first():
                db.session.add(new_pair)

        db.session.commit()
        
        if g_tuple_list.get(projID, False):
            del(g_tuple_list[projID])
        return redirect(url_for('compare'))

    return render_template('/tuple_edit.html', projName=projName, tuple_list=tuple_list)


@app.route('/tuple_edit/save', methods=['POST'])
@login_required
def pair_save():
    # pair 테이블 모두 불러온 다음 origin, comp 테이블의 절대경로를 모두 매핑.
    # originID, compID로 전체경로를 불러와 딕셔너리에 캐싱할 것.

    print(request.form.getlist('list'))

    origin_dict = {}
    comp_dict = {}
    projID = session['projID']
    tuple_list = g_tuple_list.get(projID, list())
    '''
    pairs = Pair.query.filter(Pair.projID == session['projID']).all()
    for pair in pairs:
        origin = Origin.query.filter(Origin.originID == pair.originID).first()
        if origin_dict.get(origin.originID, -1) == -1:
            origin_path = join(origin.originPath, origin.originName)
            origin_dict[origin.originID] = origin_path
        opath = origin_dict[origin.originID]

        comp = Compare.query.filter(Compare.compID == pair.compID).first()
        if comp_dict.get(comp.compID, -1) == -1:
            comp_path = join(comp.compPath, comp.compName)
            comp_dict[comp.compID] = comp_path
        cpath = comp_dict[comp.compID]

        path_list.append([opath, cpath])
    '''
    save_path = os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], session['projID']), 'pair.csv')
    with open(save_path, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(tuple_list)

    return send_file(save_path,
                     mimetype='text/csv',
                     attachment_filename='pair.csv',
                     as_attachment=True)


@app.route('/tuple_edit/load', methods=['POST'])
@login_required
def pair_load():
    # 우선 가져온 path가 실제로 존재하는지 아닌지 여부 검사
    # 검사하면서 리스트에 originID, compID 각각 저장
    # 정상적으로 검사 완료되면 비교쌍을 모두 지운다음에 다시 insert

    projID = session['projID']
    file = request.files['file']
    pair_list = []
    file_list = []

    csvReader = csv.reader(file)
    for row in csvReader:
        row = list(row)

        try:
            origin_name = row[0].rsplit('/', 1)[1]
            origin_path = row[0].rsplit('/', 1)[0]
            comp_name = row[1].rsplit('/', 1)[1]
            comp_path = row[1].rsplit('/', 1)[0]
        except:
            continue

        print (origin_path, origin_name)

        origin = Origin.query.filter(Origin.originPath == origin_path).filter(Origin.originName == origin_name).first()
        comp = Compare.query.filter(Compare.compPath == comp_path).filter(Compare.compName == comp_name).first()
        if not origin:
            continue
        if not comp:
            continue

        file_list.append(row)

        pair = Pair(origin.originID, comp.compID, projID)
        pair_list.append(pair)

    delPair = Pair.query.filter(Pair.projID == projID).all()
    for item in delPair:
        result = Result.query.filter(Result.pairID == item.pairID).all()
        for temp in result:
            db.session.delete(temp)
        db.session.delete(item)
    db.session.commit()
    '''
    for pair in pair_list:
        db.session.add(pair)
    db.session.commit()
    '''
    
    tuple_list = file_list
    
    return render_template('/tuple_edit.html', projName=session['project'], tuple_list=file_list)


@app.route('/logout', methods=['GET',   'POST'])
@login_required
def logout():
    '''
        로그아웃 및 세션 초기화
    '''
    session.clear()
    return redirect(url_for('login'))


@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return render_template('page_500.html')


@app.errorhandler(400)
def not_found(error):
    return render_template('page_403.html')


@app.errorhandler(401)
def not_found(error):
    return render_template('page_403.html')


@app.errorhandler(403)
def not_found(error):
    return render_template('page_403.html')


@app.errorhandler(404)
def not_found(error):
    return render_template('page_403.html')