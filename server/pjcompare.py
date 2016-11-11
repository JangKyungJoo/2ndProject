# -*- coding: utf-8 -*-
from os.path import join

from server import app
from server import db
from flask import render_template
from flask import request, redirect, url_for, jsonify
from flask import session
from server.models import Pair
from server.models import Result
from server.models import Origin
from server.models import Compare
from server.models import Project
from multiprocessing import Process, Queue
import time
import datetime

import filter
import sys, os
import views
import preprocessor

process_dict = {}


@app.route('/compare', methods=["GET"])
def comparePageOpen():
    projectId = getProjectId()

    project = db.session.query(Project).filter(Project.projID == projectId).first()
    print '마지막 중단 지점 : '+str(project.lastPair)

    # 초기 옵션 [ 마지막으로 비교한 비교쌍 번호, 비교 알고리즘, 주석 제거 여부, 토크나이저 종류 ]
    lastPair = 0
    compareMethod = 0
    commentRemove = 1
    tokenizer = 0

    if not os.path.exists(app.config['PROGRESS_FOLDER']):
        os.makedirs(app.config['PROGRESS_FOLDER'])

    # 저장된 지점부터 비교할 시, 메타 데이터들을 불러옴.
    if os.path.exists(join(app.config['PROGRESS_FOLDER'], str(projectId))):
        f = open(join(app.config['PROGRESS_FOLDER'], str(projectId)))
        configFile = f.read()
        configFile = eval(configFile)
        lastPair = configFile['lastPair']
        compareMethod = configFile['compareMethod']
        commentRemove = configFile['commentRemove']
        tokenizer = configFile['tokenizer']
    
    return render_template("submit.html", projectId=projectId, lastPair=lastPair,
                           compareMethod=compareMethod, commentRemove=commentRemove, tokenizer=tokenizer)


@app.route('/compare', methods=["POST"])
def compare():
    lastPair = request.form.get('lastPair')
    compareMethod = request.form.get('compareMethod')
    commentRemove = request.form.get('commentRemove')
    tokenizer = request.form.get('tokenizer')

    print commentRemove

    projectId = getProjectId()

    q = Queue()
    pr = Process(target=compareWithProcesses, args=(projectId, q, int(lastPair), int(compareMethod),
                int(commentRemove), int(tokenizer)))
    pr.daemon = True
    pr.start()

    process_dict[projectId] = [pr, q]

    numOfPair = db.session.query(Pair).filter(Pair.projID == projectId).count()
    return jsonify(numOfPair)
    # return render_template("compare.html", projectid=projectid)


def compareWithProcesses(projectId, q, lastPair, compareMethod, commentRemove, tokenizer):
    # 프로젝트 내에 있는 비교쌍들을 불러온다.
    # 비교쌍 리스트 갯수만큼 filter를 돌림.

    db.session.query(Project).filter(Project.projID == projectId).update(
        dict(compareMethod=compareMethod))

    if lastPair == 0:
        print '뿅뿅'
        for pair in db.session.query(Pair).filter(Project.projID == Pair.projID).all():
            db.session.query(Result).filter(pair.pairID == Result.pairID).delete()

    db.session.commit()

    tokenizers = {'py': preprocessor.PythonTokenizer(), 'java': preprocessor.JavaTokenizer(),
                  'c': preprocessor.CTokenizer(), 'cpp': preprocessor.CTokenizer()}

    cComment = [preprocessor.RemoveComment(token=['/*', '*/']), preprocessor.RemoveComment(token=['//', '\n'])]
    pyComment = [preprocessor.RemoveComment(token=["'''", "'''"]), preprocessor.RemoveComment(token=['"""', '"""']),
                 preprocessor.RemoveComment(token=['#', '\n'])]

    comments = {'py': pyComment, 'c': cComment, 'cpp': cComment, 'java': cComment}

    stage = 0

    pairs = db.session.query(Pair).filter(Pair.projID == projectId).all()
    for i in range(len(pairs)):
        pair = pairs[i]

        if lastPair >= pair.pairID:
            stage += 1
            continue

        tokenizerList = []
        commentList = []
        # 원본, 비교본 파일들의 경로를 얻음
        originFile = db.session.query(Origin).filter(Origin.originID == pair.originID).first()
        origin = join(originFile.originPath, originFile.originName)
        originExt = origin.rsplit('.')[0]
        tokenizerList.append(tokenizers.get(originExt, tokenizers['c']))
        commentList.append(comments.get(originExt, comments['c']))

        compFile = db.session.query(Compare).filter(Compare.compID == pair.compID).first()
        comp = join(compFile.compPath, compFile.compName)
        compExt = comp.rsplit('.')[0]
        tokenizerList.append(tokenizers.get(compExt, tokenizers['c']))
        commentList.append(comments.get(compExt, comments['c']))

        # 옵션 인자들과 함께 원본과 비교본의 경로를 넘겨 두 파일을 실제 비교하게 함.
        if tokenizer == 0:
            tokenizerList = [preprocessor.SpaceTokenizer(), preprocessor.SpaceTokenizer()]
        if commentRemove == 0:
            commentList = []

        filter.compareOnePair(origin, comp, pair.pairID, compareMethod, commentList
                              , tokenizerList)
        db.session.query(Project).filter(Project.projID == projectId).update(
            dict(lastPair=pair.pairID))
        db.session.commit()

        # 비교 진행 상황을 파일에 저장
        f = open(join(app.config['PROGRESS_FOLDER'], str(projectId)), 'w')
        f.write(str({'lastPair': pair.pairID, 'compareMethod': compareMethod, 'commentRemove': commentRemove,
                     'tokenizer': tokenizer}))

        # 취소 확인

        q.put(stage)
        lastPair = pair.pairID
        stage += 1
        # print "put : " + str(pair.pairID)

    if os.path.exists(join(app.config['PROGRESS_FOLDER'], str(projectId))):
        os.remove(join(app.config['PROGRESS_FOLDER'], str(projectId)))
    db.session.commit()
    q.put(stage)


@app.route("/compare/state", methods=["GET"])
def processState():
    projectId = getProjectId()

    process_set = process_dict.get(projectId, -1)
    if process_set == -1:
        return -1
    q = process_set[1]

    currentNumber = -1

    while True:
        try:
            currentNumber = q.get(block=False)
        except:
            break

    # print currentNumber
    return jsonify(currentNumber)


@app.route("/compare/cancel", methods=["POST"])
def cancelCompare():
    projectId = getProjectId()

    pr = process_dict[projectId][0]
    print pr, pr.is_alive()
    pr.terminate()
    pr.join()

    del (process_dict[projectId])

    return redirect('/dashboard')


def getProjectId():
    #if not session['project'] or session['project'] == "":
    if not session['projID'] or session['projID'] is None:
        return redirect(url_for('dashboard'))
    else:
        return session['projID']
    '''
    else:
        projID = session['project']

    project = db.session.query(Project).filter(Project.projName == projName).first()
    projectId = project.projID

    return projectId
    '''