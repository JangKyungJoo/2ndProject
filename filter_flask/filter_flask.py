# -*- coding-utf8 -*-

from flask import Flask, render_template, request
import filter

import sys

app = Flask(__name__)

taskList = []
taskDict = {}
taskArgs = []


@app.route('/', methods=['GET'])
def hello_world():
    return render_template('file_select.html')


@app.route('/file', methods=['POST'])
def temp():
    global taskList, taskArgs, taskDict, output

    originFile = request.files['originfile']
    compFile = request.files['compfile']

    originFile = originFile.stream.read()
    compFile = compFile.stream.read()

    # ft = filter.Hi(originFile, compFile)
    lineNumInfo = []
    for i in range(len(originFile.split('\n'))):
        lineNumInfo.append(i)
    '''
    ft = filter.Filter(originFile)
    ft.file, list = ft.deleteComment(['//', '\n'], list)
    ft.file, list = ft.deleteComment(['/*', '*/'], list)
    ft.file, list = filter.deleteLineFeed(ft.file, list)
    ft.file, list = ft.tokenizing(list)
    '''

    rc = filter.RemoveComment()
    rc.setInput([originFile, ['/*', '*/']])
    rc.setLineNumInfo(lineNumInfo)
    originFile, list = rc.process()

    # print ft.file, list
    # for i in range(len(ft.file)):
    # print i+1, ft.file[i]
    # file = ft.tokenizing()
    # for i in range(len(file)):
    # print i+1, file[i]

    preprocess_filter = [filter.RemoveComment(), filter.RemoveBlank(), filter.Tokenizing()]

    inputs = [[originFile, ['/*', '*/']], [compFile, ['/*', '*/']]]
    outputs = []
    for input in inputs:
        for task in preprocess_filter:
            task.setInput(input)
            task.setLineNumInfo(lineNumInfo)
            output, lineNumInfo = task.process()
            input = output
        outputs.append([output, lineNumInfo])

    for i in range(len(outputs[1][0])):
        print i+1, outputs[1][0][i], outputs[1][1][i]+1

    checkFunction = filter.OrderedCheck()

    compare = filter.Compare(checkFunction)
    compare.setInput(outputs[0][0], outputs[1][0])
    ret = compare.process()

    print ret

    return ''


if __name__ == '__main__':
    app.run()
