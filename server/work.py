#-*- coding: utf-8 -*-

import requests
import time
from flask import render_template
from flask import request
from server import app
from server import preprocessor
from server.filter import compareOnePair

port = 3001
requests.get('http://0.0.0.0:5000/worker/' + str(port))


@app.route('/work', methods=["POST"])
def work():
    tokenizers = {'py': preprocessor.PythonTokenizer(), 'java': preprocessor.JavaTokenizer(),
                  'c': preprocessor.CTokenizer(), 'cpp': preprocessor.CTokenizer()}

    cComment = [preprocessor.RemoveComment(token=['/*', '*/']), preprocessor.RemoveComment(token=['//', '\n'])]
    pyComment = [preprocessor.RemoveComment(token=["'''", "'''"]), preprocessor.RemoveComment(token=['"""', '"""']),
                 preprocessor.RemoveComment(token=['#', '\n'])]

    comments = {'py': pyComment, 'c': cComment, 'cpp': cComment, 'java': cComment}

    tokenizerList = []
    commentList = []

    data = request.get_json(force=True)

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
    compareOnePair(data['origin'], data['comp'], data['pairID'], data['compareMethod'], commentList,tokenizerList, data['lineNum'])
    return 'ok'


def getOrigin(originID):
    res = requests.get('http://0.0.0.0:5000/origin/' + str(originID))
    return res.content


def getCompare(compID):
    res = requests.get('http://0.0.0.0:5000/compare/' + str(compID))
    return res.content


@app.route('/alive', methods=["GET"])
def alive():
    print 'get'
    return 'ok'

# 포트번호 : 3000 ~ 3004
app.run(debug=True, host='0.0.0.0', port=port)