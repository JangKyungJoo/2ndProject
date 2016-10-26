#-*- coding: utf-8 -*-
from flask import Flask, request, render_template
from server import app
from flask import json
from datetime import datetime
from server.models import Pair
from server.models import Result
import urllib2
import socket
from flask import session
from server import db
from werkzeug import secure_filename


@app.route('/result/<projectid>', methods=["GET"])
def result(projectid):

    pair = Pair.query.filter(Pair.projID == projectid).order_by(Pair.similarity.desc(), Pair.modifyDate).all()
    json_list = [i.serialize for i in pair]

    pair = Pair.query.filter(Pair.projID == projectid).order_by(Pair.similarity.desc(), Pair.modifyDate.desc()).all()
    json_list2 = [i.serialize for i in pair]

    return render_template("result.html", dateByAsc=json.dumps(json_list), dateByDesc=json.dumps(json_list2), pairCount=len(pair), projectid=projectid)


@app.route('/result/<projectid>/<pairid>', methods=["GET"])
def detail(projectid, pairid):
    if request.method == 'GET':
        origin = open("/Users/kyungjoo/Documents/Document/Maestro-backend/maestro/routes/board.js", 'r')
        compare = open("/Users/kyungjoo/Documents/Document/Maestro-backend/maestro/routes/anonymity.js", 'r')
        originList = []
        compareList = []
        lines = origin.readlines()
        for line in lines:
            originList.append(line)
        lines = compare.readlines()
        for line in lines:
            compareList.append(line)

        result = Result.query.filter(Result.pairID == 1).order_by(Result.originLine).all()
        list = [i.serialize for i in result]

        # 원본소스코드 / 비교본 소스코드 / 원본 기준 결과
        return render_template\
            ("detail.html", origin=originList, originCount=len(originList), compare=compareList, list=json.dumps(list))
    """
    if request.method == 'POST':
        #req = urllib2.Request("http://0.0.0.0:5000/result/1/1")
        url = 'https://api.github.com/users?since=100'

        try:
            #res = urllib2.urlopen(req)
            output = json.load(urllib2.urlopen(url))
            print(output)
        except urllib2.URLError as e:
            print e.reason
            print e.code
        except socket.timeout as e:
            print e.reason
            print e.code
        except urllib2.HTTPError as e:
            print e.reason
            print 'Error code: ', e.code
        else:
            #data = json.load(res.read())
            #print data
            return render_template("detail.html")
    """

# DB 초기화에 대비한 db add 부분. 지울 것
@app.route('/init/pair', methods=["GET"])
def init_pair():
    """
    for i in range(1, 51):
        pair = Pair(i, i, 1)
        db.session.add(pair)
        db.session.commit()
    """
    temp = [89.12, 56.23, 94.01, 66.66, 72.44, 48.38, 29.75, 80.09, 76.92, 81.38]
    i = 0
    pair = Pair.query.filter(Pair.projID==1).all()
    for line in pair:
        line.similarity = temp[i%10]
        if i%3==0:
            line.modifyDate = datetime.now()
        i+=1
        db.session.add(line)
        db.session.commit()

    return render_template("result.html")


@app.route('/init/result', methods=["GET"])
def init_detail():
    origin = open("/Users/kyungjoo/Documents/Document/Maestro-backend/maestro/routes/board.js", 'r')
    compare = open("/Users/kyungjoo/Documents/Document/Maestro-backend/maestro/routes/anonymity.js", 'r')
    charToken = [',', '.', '/', ';', '*', '(', ')', '-', '_', '&', '%']
    originList = []
    compareList = []
    lines = origin.readlines()
    for line in lines:
        originList.append(line)
    lines = compare.readlines()
    for line in lines:
        compareList.append(line)
    SAME = 1;
    SIMILAR = 2;

    similarLineCount = 0
    sameLineCount = 0
    originlineNum = 1
    comparelineNum = 1
    tempPercent = 0
    result = []  # 원본라인 / 비교본라인 / 유형(동일, 유사)

    for oline in originList:
        if oline != "":
            for cline in compareList:
                if cline != "":
                    oword = oline.split()
                    cword = cline.split()
                    tokenCount = 0
                    for otoken in oword:
                        for ctoken in cword:
                            if otoken == ctoken and otoken not in charToken:
                                tokenCount += 1
                    # 완전 일치
                    if tokenCount >= 2 and tokenCount == len(oword):
                        print('same : %d, %d' % (originlineNum, comparelineNum))
                        if len(result) == 0:
                            result.append([originlineNum, comparelineNum, SAME])
                            sameLineCount += 1
                        elif result[len(result) - 1][0] == originlineNum:
                            result[len(result) - 1] = [originlineNum, comparelineNum, SAME]
                        else:
                            result.append([originlineNum, comparelineNum, SAME])
                            sameLineCount += 1

                    # 유사
                    elif tokenCount > 2 and (tokenCount / len(oword)) > 0.3:
                        print ('similar : %d, %d' % (originlineNum, comparelineNum))
                        if len(result) == 0:
                            result.append([originlineNum, comparelineNum, SIMILAR])
                            similarLineCount += 1
                        elif result[len(result) - 1][0] == originlineNum:
                            if tokenCount / len(oword) > tempPercent:
                                result[len(result) - 1] = [originlineNum, comparelineNum, SIMILAR]
                        else:
                            result.append([originlineNum, comparelineNum, SIMILAR])
                            similarLineCount += 1

                comparelineNum += 1
            comparelineNum = 1
            tempPercent = 0
        originlineNum += 1

    for line in result:
        print line
        temp = Result(1, line[0], line[1], 1, line[2])
        db.session.add(temp)
        db.session.commit()

    return render_template("result.html")