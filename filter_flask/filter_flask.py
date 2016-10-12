# -*- coding-utf8 -*-

from flask import Flask, render_template, request
import filter

import sys

from server import db

sys.path.append('../')
from server.models import Result

app = Flask(__name__)


taskList = []
taskDict = {}
taskArgs = []


@app.route('/', methods=['GET'])
def hello_world():
    return render_template('file_select.html')


@app.route('/file', methods=['POST'])
def temp():
    global taskList, taskArgs, taskDict

    originFile = request.files['originfile']
    compFile = request.files['compfile']

    originFile = originFile.stream.read()
    compFile = compFile.stream.read()

    ft = filter.Hi(originFile, compFile)

    checkFunction = filter.OrderedCheck(ft.originToken, ft.compToken)

    taskList = [ft.deleteComment, ft.calcSimilarity]
    taskDict = {ft.calcSimilarity: [ft.tokenizing], ft.tokenizing: [ft.listing]}
    taskArgs = {ft.deleteComment: [('//', '\n'), ('/*', '*/')], ft.listing: [()],
                ft.tokenizing: [()], ft.calcSimilarity: [(checkFunction,)]}

    for task in taskList:
        res = process(task)

    print res

    new_result = Result(originFile, compFile, res[1], 1)
    db.session.add(new_result)
    db.session.commit()

    del ft
    del checkFunction

    return str(res)


def process(task):
    for n in taskDict.get(task, []):
        process(n)

    for argument in taskArgs[task]:
        res = task(*argument)

    return res

if __name__ == '__main__':
    app.run()
