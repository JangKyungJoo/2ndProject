# -*- coding: utf-8 -*-

import requests
import time
from flask import render_template
from flask import request
from flask import json
from server import app
from server import preprocessor
from server.filter import compareOnePair
from threading import Thread, Lock, Event
from Queue import Queue

from signal import signal, SIGPIPE, SIG_IGN
signal(SIGPIPE, SIG_IGN)

lock = Lock()
taskQueueList = {}
threadList = {}

a = 0

port = 3000
requests.get('http://0.0.0.0:5000/worker/' + str(port))


@app.route('/work', methods=["POST"])
def work():
    data = request.get_json(force=True)
    taskQueueList[data['projectId']].put(data)
    threadList[data['projectId']][1].set()

    return 'ok'


def process(e, projectId):
    global lock
    while True:
        if taskQueueList[projectId].empty():
            e.wait()
        if threadList[projectId][2] == 1:
            break
        data = taskQueueList[projectId].get()

        tokenizers = {'py': preprocessor.PythonTokenizer(), 'java': preprocessor.JavaTokenizer(),
                      'c': preprocessor.CTokenizer(), 'cpp': preprocessor.CTokenizer()}

        cComment = [preprocessor.RemoveComment(token=['/*', '*/']), preprocessor.RemoveComment(token=['//', '\n'])]
        pyComment = [preprocessor.RemoveComment(token=["'''", "'''"]), preprocessor.RemoveComment(token=['"""', '"""']),
                     preprocessor.RemoveComment(token=['#', '\n'])]

        comments = {'py': pyComment, 'c': cComment, 'cpp': cComment, 'java': cComment}

        tokenizerList = []
        commentList = []

        originExt = data['origin'].rsplit('.')[1]
        tokenizerList.append(tokenizers.get(originExt, tokenizers['c']))
        commentList.append(comments.get(originExt, comments['c']))
        compExt = data['comp'].rsplit('.')[1]
        tokenizerList.append(tokenizers.get(compExt, tokenizers['c']))
        commentList.append(comments.get(compExt, comments['c']))

        if data['tokenizer'] == 0:
            tokenizerList = [preprocessor.SpaceTokenizer(), preprocessor.SpaceTokenizer()]
        if data['commentRemove'] == 0:
            commentList = []

        result = compareOnePair(getOrigin(data['originID']), getCompare(data['compID']), data['pairID'],
                                data['compareMethod'],
                                commentList, tokenizerList, data['lineNum'], data['blockSize'])
        res = requests.post('http://0.0.0.0:5000/done', json=json.dumps(result))
        if res == 'end':
            break

        if threadList[projectId][2] == 1:
            del (threadList[projectId])
            del (taskQueueList[projectId])
            break


def getOrigin(originID):
    res = requests.get('http://0.0.0.0:5000/origin/' + str(originID))
    return res.content


def getCompare(compID):
    res = requests.get('http://0.0.0.0:5000/compare/' + str(compID))
    return res.content


@app.route('/work_start', methods=["POST"])
def workStart():
    projectId = request.get_data()

    taskQueueList[int(projectId)] = Queue()
    event = Event()
    t = Thread(target=process, args=(event, int(projectId)))
    # 각각 스레드 객체, 이벤트 객체, 종료 플래그
    threadList[int(projectId)] = [t, event, 0]
    t.start()

    return 'ok'


@app.route('/work_cancel', methods=["POST"])
def workCancel():
    projectId = request.get_data()

    threadList[int(projectId)][1].set()
    threadList[int(projectId)][2] = 1
    # threadList[int(projectId)][0].join()

    return 'ok'


# 포트번호 : 3000 ~ 3004
app.run(debug=True, host='0.0.0.0', port=port)
