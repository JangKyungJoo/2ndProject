#-*- coding: utf-8 -*-
from flask import Flask, request, render_template
from server import app
from flask import json
from datetime import datetime
from server.models import Pair
from server.models import Project
from server.models import Result
from server.models import Origin
from server.models import Compare
from server.models import People
from server import db


@app.route('/result/<projectid>', methods=["GET"])
def result(projectid):

    print 'pair'
    pair = Pair.query.filter(Pair.projID == projectid)
    for line in pair:
        print '%d %d' %(line.originID, line.compID)

    #origin_list = Origin.query.with_entities(Origin.originName).filter(Origin.projID == projectid).all()
    #compare_list = Compare.query.with_entities(Compare.compName).filter(Compare.projID == projectid).all()

    origin_list = Origin.query.filter(Origin.projID == projectid).all()
    compare_list = Compare.query.filter(Compare.projID == projectid).all()

    print 'origin'
    for origin in origin_list:
        print '%d %s' %(origin.originID, origin.originName)

    print 'compare'
    for compare in compare_list:
        print '%d %s' %(compare.compID, compare.compName)

    pair = Pair.query.filter(Pair.projID == projectid).order_by(Pair.similarity.desc()).all()
    json_list = [Pair.serialize(i, origin_list[i.originID-1], compare_list[i.compID-1]) for i in pair]

    pair = Pair.query.filter(Pair.projID == projectid).order_by(Pair.similarity.desc(), Pair.modifyDate.desc()).all()
    json_list2 = [Pair.serialize(i, origin_list[i.originID-1], compare_list[i.compID-1]) for i in pair]

    print 'pair count : %d' %len(pair)

    #return render_template("result.html", dateByAsc=json.dumps(json_list), dateByDesc=json.dumps(json_list2), pairCount=len(pair), projectid=projectid)
    return render_template("temp.html", dateByAsc=json.dumps(json_list), dateByDesc=json.dumps(json_list2),
                           pairCount=len(pair), projectid=projectid)


@app.route('/result/<projectid>/<pairid>', methods=["GET", "POST"])
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

        pairid = 1
        result = Result.query.filter(Result.pairID == pairid).order_by(Result.originLine).all()
        list = [i.serialize for i in result]

        # 원본소스코드 / 비교본 소스코드 / 원본 기준 결과
        return render_template("detail.html", origin=originList, originCount=len(originList), compare=compareList, list=json.dumps(list), pairid = pairid)

    if request.method == 'POST':

        data = request.data
        update = json.loads(data)
        pairid = 1
        REMOVE = 3
        ADD = 4

        for line in update:
            if line['type'] == REMOVE:
                delete = Result.query.filter(Result.pairID==pairid).filter(Result.originLine==line['originLine']).filter(Result.compLine==line['compLine']).first()
                db.session.delete(delete)
                db.session.commit()
            elif line['type'] == ADD:
                add = Result(pairid, line['originLine'], line['compLine'], 1)
                db.session.add(add)
                db.session.commit()

        pair = Pair.query.get(pairid)
        pair.modifyDate = datetime.now()
        db.session.add(pair)
        db.session.commit()

        return render_template("detail.html")


# DB 초기화에 대비한 db add 부분. 지울 것
@app.route('/init', methods=["GET"])
def init_pair():
    people = People('KyungJoo', 'rudwn826@naver.com', '1234')
    db.session.add(people)
    db.session.commit()
    '''
    for i in range(1, 51):
        pair = Pair(i, i, 1)
        db.session.add(pair)
        db.session.commit()

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

    init_detail()
    init_file()
    '''
    return render_template("temp.html")


def init_file():
    temp1 = ["MainActivity.java", "MainFragment.java", "SearchActivity.java", "OriginActivity.java", "CompareActivity.java", "Service.java"]
    temp2 = ["Model.java", "ModelView.java", "SearchView.java", "Network.java", "SearchFragment.java", "Controller.java"]

    for i in range(1, 51):
        origin = Origin(temp1[i%6], "C:", 140, 1)
        db.session.add(origin)
        db.session.commit()
        compare = Compare(temp2[i%6], "D:", 140, 1)
        db.session.add(compare)
        db.session.commit()


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
        temp = Result(1, line[0], line[1], line[2])
        db.session.add(temp)
        db.session.commit()