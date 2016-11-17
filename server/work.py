#-*- coding: utf-8 -*-

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

lock = Lock()
taskQueue = Queue()
threadList = []
a = 0


@app.route('/work', methods=["POST"])
def work():
    data = request.get_json(force=True)
    taskQueue.put(data)
    global a
    print a
    a += 1

    for i in range(0, 10):
        threadList[i][1].set()

    return 'ok'


def process(e):
    global lock
    while True:
        lock.acquire()
        if taskQueue.empty():
            e.wait()
        data = taskQueue.get()
        lock.release()

        tokenizers = {'py': preprocessor.PythonTokenizer(), 'java': preprocessor.JavaTokenizer(),
                    'c': preprocessor.CTokenizer(), 'cpp': preprocessor.CTokenizer()}

        cComment = [preprocessor.RemoveComment(token=['/*', '*/']), preprocessor.RemoveComment(token=['//', '\n'])]
        pyComment = [preprocessor.RemoveComment(token=["'''", "'''"]), preprocessor.RemoveComment(token=['"""', '"""']),
                    preprocessor.RemoveComment(token=['#', '\n'])]

        comments = {'py': pyComment, 'c': cComment, 'cpp': cComment, 'java': cComment}

        tokenizerList = []
        commentList = []

        originExt = data['origin'].rsplit('.')[0]
        tokenizerList.append(tokenizers.get(originExt, tokenizers['c']))
        commentList.append(comments.get(originExt, comments['c']))
        compExt = data['comp'].rsplit('.')[0]
        tokenizerList.append(tokenizers.get(compExt, tokenizers['c']))
        commentList.append(comments.get(compExt, comments['c']))

        if data['tokenizer'] == 0:
            tokenizerList = [preprocessor.SpaceTokenizer(), preprocessor.SpaceTokenizer()]
        if data['commentRemove'] == 0:
            commentList = []

        print 'receive : ' + str(data['origin']) + ', ' + str(data['comp']) + ', ' + str(data['pairID']) + ', ' + str(data['compareMethod']) + ', ' + str(data['lineNum'])
        # result를 리턴값으로 받아와서 이 함수 내에서 post전송
        result = compareOnePair(data['origin'], data['comp'], data['pairID'], data['compareMethod'], commentList,tokenizerList, data['lineNum'])
        res = requests.post('http://0.0.0.0:5000/done', json=json.dumps(result))


for i in range(0, 10):
    event = Event()
    t = Thread(target=process, args=(event,))
    threadList.append([t, event])
    t.start()


def getOrigin(originID):
    res = requests.get('http://0.0.0.0:5000/origin/' + str(originID))
    return res.content


def getCompare(compID):
    res = requests.get('http://0.0.0.0:5000/compare/' + str(compID))
    return res.content

app.run(debug=True, host='0.0.0.0', port=8888)