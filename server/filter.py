# coding=utf-8
# -*- coding-utf8 -*-

import preprocessor
import compare
import os
from server.models import Result
from server import db
from server import app


def temp():
    global output
    originFile = open("/Users/user/PycharmProjects/filter_flask/ex/4340897.c")
    compFile = open("/Users/user/PycharmProjects/filter_flask/ex/4370143.c")

    originFile = originFile.read()
    compFile = compFile.read()

    preprocess_filter = [preprocessor.RemoveComment(token=['/*', '*/']), preprocessor.RemoveBlank(),
                         preprocessor.Tokenizing()]

    inputs = [originFile, compFile]
    outputs = []

    for input in inputs:
        lineNumInfo = []
        for i in range(len(input.split('\n'))):
            lineNumInfo.append(i)

        for task in preprocess_filter:
            task.setInput(input)
            task.setLineNumInfo(lineNumInfo)
            output, lineNumInfo = task.process()
            input = output

        outputs.append([output, lineNumInfo])

    # ori, comp = preprocessor.numberMapping(outputs[0][0], outputs[1][0])


    checkFunction = compare.OrderedCheck()

    compa = compare.Compare(checkFunction)
    compa.setInput(outputs[0][0], outputs[1][0])
    ret = compa.process()

    print ret

    db.drop_all()
    db.create_all()

    for key in ret.keys():
        # key : 원본 라인 번호 - 1
        print key
        for element in ret[key]:
            # element : [원본 key라인과 매칭된 비교본 라인번호, 유사타입(1 : 일치, 2 : 유사)
            print element
            newResult = Result(3, outputs[0][1][key]+1, outputs[1][1][element[0]]+1, 1, element[1])
            db.session.add(newResult)
    db.session.commit()

    for u in db.session.query(Result).all():
        print(u.resultID, u.pairID, u.originLine, u.compLine, u.count, u.rType)



temp()
