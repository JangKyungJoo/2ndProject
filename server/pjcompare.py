# -*- coding: utf-8 -*-
from os.path import join

from datetime import datetime
import requests
from flask import json
from pywebhdfs.webhdfs import PyWebHdfsClient
from subprocess import call
from flask import send_file
from server import manager
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
import sys, os
import preprocessor


process_dict = {}

# 프로세스 고유 변수
stageList = {}
paramList = {}
pairCount = {}


@app.route('/compare', methods=["GET"])
def comparePageOpen():
    projectId = getProjectId()

    # 초기 옵션 [ 마지막으로 비교한 비교쌍 번호, 비교 알고리즘, 주석 제거 여부, 토크나이저 종류 ]
    lastPair = 0
    compareMethod = 0
    commentRemove = 1
    tokenizer = 0
    blockSize = 1

    '''
        sync hdfs storage with local storage

        $ hdfs dfs -put -f 'app.config['UPLOAD_FOLDER'] /
    '''
    call(["hdfs", "dfs", "-put", "-f", app.config['UPLOAD_FOLDER'], "/"])

    if not os.path.exists(app.config['PROGRESS_FOLDER']):
        os.makedirs(app.config['PROGRESS_FOLDER'])

    # 저장된 지점부터 비교할 시, 메타 데이터들을 불러옴.
    if os.path.exists(join(app.config['PROGRESS_FOLDER'], str(projectId))):
        f = open(join(app.config['PROGRESS_FOLDER'], str(projectId)))
        configFile = f.read()
        configFile = eval(configFile)
        lastPair = configFile['stageList']
        compareMethod = configFile['compareMethod']
        commentRemove = configFile['commentRemove']
        tokenizer = configFile['tokenizer']
        blockSize = configFile['blockSize']

        stageList[int(projectId)] = lastPair
    else:
        stageList[int(projectId)] = []

    # print lastPair

    return render_template("submit.html", projectId=projectId, lastPair=lastPair,
                           compareMethod=compareMethod, commentRemove=commentRemove, tokenizer=tokenizer,
                           blockSize=blockSize)


@app.route('/compare', methods=["POST"])
def compare():
    lastPair = request.form.get('lastPair')
    compareMethod = request.form.get('compareMethod')
    commentRemove = request.form.get('commentRemove')
    tokenizer = request.form.get('tokenizer')
    blockSize = request.form.get('blockSize')

    lastPair = json.loads(lastPair)

    projectId = getProjectId()

    q = Queue()
    paramList[int(projectId)] = [q, compareMethod, commentRemove, tokenizer, blockSize]
    # 각 노드에 분배하는 부분은 별도 프로세스에서 수행
    pr = Process(target=compareWithProcesses, args=(projectId, q, lastPair, int(compareMethod),
                int(commentRemove), int(tokenizer), int(blockSize)))
    pr.daemon = True
    pr.start()

    process_dict[int(projectId)] = [pr, q]

    numOfPair = db.session.query(Pair).filter(Pair.projID == projectId).count()
    pairCount[int(projectId)] = numOfPair
    return jsonify(numOfPair)


def compareWithProcesses(projectId, q, lastPair, compareMethod, commentRemove, tokenizer, blockSize):
    # 프로젝트 내에 있는 비교쌍들을 불러온다.
    # 비교쌍 리스트 갯수만큼 filter를 돌림.

    projectId = getProjectId()
    stage = []
    print lastPair
    if not lastPair:
        for pair in db.session.query(Pair).filter(Project.projID == Pair.projID).all():
            db.session.query(Result).filter(pair.pairID == Result.pairID).delete()
        if os.path.exists(join(app.config['PROGRESS_FOLDER'], str(projectId))):
            os.remove(join(app.config['PROGRESS_FOLDER'], str(projectId)))
    else:
        stage = lastPair

    db.session.commit()

    tokenizers = {'py': preprocessor.PythonTokenizer(), 'java': preprocessor.JavaTokenizer(),
                  'c': preprocessor.CTokenizer(), 'cpp': preprocessor.CTokenizer()}

    cComment = [preprocessor.RemoveComment(token=['/*', '*/']), preprocessor.RemoveComment(token=['//', '\n'])]
    pyComment = [preprocessor.RemoveComment(token=["'''", "'''"]), preprocessor.RemoveComment(token=['"""', '"""']),
                 preprocessor.RemoveComment(token=['#', '\n'])]

    comments = {'py': pyComment, 'c': cComment, 'cpp': cComment, 'java': cComment}

    workerList = manager.worker_list
    for worker in workerList:
        target = 'http://0.0.0.0:' + str(worker) + '/work_start'
        res = requests.post(target, data=projectId)

    pairs = db.session.query(Pair).filter(Pair.projID == projectId).all()
    for i in range(len(pairs)):
        # print '단계 : ', i
        pair = pairs[i]

        if pair.pairID in stage:
            continue

        tokenizerList = []
        commentList = []
        # 원본, 비교본 파일들의 경로를 얻음
        originFile = db.session.query(Origin).filter(Origin.originID == pair.originID).first()
        origin = join(originFile.originPath, originFile.originName)
        originExt = origin.rsplit('.')[0]
        tokenizerList.append(tokenizers.get(originExt, tokenizers['c']))
        commentList.append(comments.get(originExt, comments['c']))
        originLineNumber = originFile.lineNum

        compFile = db.session.query(Compare).filter(Compare.compID == pair.compID).first()
        comp = join(compFile.compPath, compFile.compName)
        compExt = comp.rsplit('.')[0]
        tokenizerList.append(tokenizers.get(compExt, tokenizers['c']))
        commentList.append(comments.get(compExt, comments['c']))

        # 각 노드에
        compare = {'origin': origin, 'comp': comp, 'pairID': pair.pairID, 'compareMethod' : compareMethod,
                   'tokenizer': tokenizer, 'commentRemove' : commentRemove, 'lineNum' : originLineNumber,
                   'blockSize': blockSize, 'originID' : pair.originID, 'compID' : pair.compID, 'projectId': pair.projID}
        if manager.get_worker() != -1:
            target = 'http://0.0.0.0:' + str(manager.get_worker()) + '/work'
            res = requests.post(target, json=compare)
    print '끝'
    db.session.commit()


@app.route("/compare/state", methods=["GET"])
def processState():
    projectId = getProjectId()
    # 몇개 비교했는지 리턴
    currentNumber = len(stageList[int(projectId)])
    # print currentNumber

    # 비교가 끝났을 경우, 자원 해제하고 파일 제거
    if pairCount[int(projectId)] == currentNumber:
        del stageList[int(projectId)]
        del paramList[int(projectId)]
        del pairCount[int(projectId)]
        if os.path.exists(join(app.config['PROGRESS_FOLDER'], str(projectId))):
            os.remove(join(app.config['PROGRESS_FOLDER'], str(projectId)))

    return jsonify(currentNumber)


@app.route("/compare/cancel", methods=["POST"])
def cancelCompare():
    projectId = getProjectId()

    pr = process_dict[int(projectId)][0]
    pr.terminate()
    pr.join()

    workerList = manager.worker_list
    for worker in workerList:
        target = 'http://0.0.0.0:' + str(worker) + '/work_cancel'
        res = requests.post(target, data=projectId)

    del (process_dict[int(projectId)])

    return redirect('/dashboard')


def getProjectId():
    if not session['projID'] or session['projID'] is None:
        return redirect(url_for('dashboard'))
    else:
        return session['projID']


@app.route("/done", methods=["POST"])
def done():
    global stageList
    global paramList

    data = request.get_json(force=True)
    result = json.loads(data)
    #print result

    pairId = result[0][0]
    similarity = result[0][1]
    pair = Pair.query.filter(Pair.pairID == pairId).first()

    result = result[1:]

    stageList[pair.projID].append(pairId)

    # 비교 진행 상황을 파일에 저장
    f = open(join(app.config['PROGRESS_FOLDER'], str(pair.projID)), 'w')
    f.write(str({'stageList': stageList[pair.projID], 'compareMethod': paramList[pair.projID][1],
                 'commentRemove': paramList[pair.projID][2], 'tokenizer': paramList[pair.projID][3],
                 'blockSize': paramList[pair.projID][4]}))
    f.close()

    for r in result:
        newResult = Result(pairId, r['originLine'], r['compareLine'], r['rType'])
        db.session.add(newResult)

    pair = db.session.query(Pair).filter(Pair.pairID == pairId).first()
    pair.similarity = similarity
    pair.modifyDate = datetime.now()
    db.session.commit()

    projectId = int(pair.projID)
    currentNumber = len(stageList[int(projectId)])
    # print currentNumber

    if pairCount.get(int(projectId), -1) == currentNumber:
        if os.path.exists(join(app.config['PROGRESS_FOLDER'], str(projectId))):
            os.remove(join(app.config['PROGRESS_FOLDER'], str(projectId)))

        del (process_dict[int(projectId)])

        return 'end'

    return 'ok'


@app.route('/origin/<fileid>', methods=["GET"])
def getOrigin(fileid):
    '''

        hdfs applied
        flask.send_file -> hdfs.read_file

        :param fileid:
        :return:
    '''
    hdfs = PyWebHdfsClient(host='localhost', port='50070')
    origin = Origin.query.filter(Origin.originID == fileid).first()
    path = join(origin.originPath, origin.originName)
    path = path.replace(app.config['UPLOAD_FOLDER'], "")
    path = "/uploads" + str(path)
    # return send_file(path)
    return hdfs.read_file(path)


@app.route('/compare/<fileid>', methods=["GET"])
def getCompare(fileid):
    '''

        hdfs applied
        flask.send_file -> hdfs.read_file

        :param fileid:
        :return:
    '''
    hdfs = PyWebHdfsClient(host='localhost', port='50070')
    compare = Compare.query.filter(Compare.compID == fileid).first()
    path = join(compare.compPath, compare.compName)
    path = path.replace(app.config['UPLOAD_FOLDER'], "")
    path = "/uploads" + str(path)
    # return send_file(path)
    return hdfs.read_file(path)