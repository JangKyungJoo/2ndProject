#-*- coding: utf-8 -*-
import os

from flask import Flask, request, render_template
from flask import redirect
from flask import url_for
from server import app
from flask import json
from datetime import datetime
from server.models import Pair
from server.models import Project
from server.models import Result
from server.models import Origin
from server.models import Compare
from server.models import People
from flask import session
from server import db
import codecs

@app.route('/result', methods=["GET"])
def default():
    if not session['project'] or session['project'] == "":
        return redirect(url_for('dashboard'))
    else:
        projName = session['project']
        project_data = Project.query.filter(Project.projName==projName).first()
        projID = project_data.projID
        return redirect('result/' + str(projID))


@app.route('/result/<projectid>', methods=["GET"])
def result(projectid):

    project = Project.query.get(projectid)
    projName = project.projName

    pair = Pair.query.filter(Pair.projID == projectid).order_by(Pair.similarity.desc()).all()
    json_list = [Pair.serialize(i, Origin.query.with_entities(Origin.originName).filter(Origin.projID == projectid).filter(Origin.originID == i.originID).first(), Compare.query.with_entities(Compare.compName).filter(Compare.projID == projectid).filter(Compare.compID == i.compID).first()) for i in pair]

    pair = Pair.query.filter(Pair.projID == projectid).order_by(Pair.similarity.desc(), Pair.modifyDate.desc()).all()
    json_list2 = [Pair.serialize(i, Origin.query.with_entities(Origin.originName).filter(Origin.projID == projectid).filter(Origin.originID == i.originID).first(),Compare.query.with_entities(Compare.compName).filter(Compare.projID == projectid).filter(Compare.compID == i.compID).first()) for i in pair]

    return render_template("result.html", dateByAsc=json.dumps(json_list), dateByDesc=json.dumps(json_list2), pairCount=len(pair), projectid=projectid, projName = projName)


@app.route('/result/<projectid>/<pairid>', methods=["GET", "POST"])
def detail(projectid, pairid):
    if request.method == 'GET':

        pair = Pair.query.get(pairid)

        origin = Origin.query.filter(Origin.originID == pair.originID).first()
        compare = Compare.query.filter(Compare.compID == pair.compID).first()

        originPath = os.path.join(origin.originPath, origin.originName)
        comparePath = os.path.join(compare.compPath, compare.compName)

        originFile = codecs.open(originPath, 'r', 'utf-8', 'ignore')
        compFile = codecs.open(comparePath, 'r', 'utf-8', 'ignore')

        originList = []
        compareList = []

        lines = originFile.readlines()
        for line in lines:
            originList.append(line)

        lines = compFile.readlines()
        for line in lines:
            compareList.append(line)

        result = Result.query.filter(Result.pairID == pairid).order_by(Result.originLine).all()
        list = [i.serialize for i in result]

        # 원본소스코드 / 비교본 소스코드 / 원본 기준 결과
        return render_template("detail.html", origin=originList, originCount=len(originList), compare=compareList, list=json.dumps(list), pairid = pairid, originPath = getPath(originPath), compPath = getPath(comparePath))

    if request.method == 'POST':

        data = request.data
        update = json.loads(data)
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
        origin = Origin.query.filter(Origin.originID == pair.originID).first()
        originLine = origin.lineNum
        count = Result.query.filter(Result.pairID == pair.pairID).count()

        pair.similarity = count * 100 / originLine
        pair.modifyDate = datetime.now()
        db.session.add(pair)
        db.session.commit()

        return render_template("detail.html")

def getPath(path):
    temp = path[len(app.config['UPLOAD_FOLDER']):]
    return temp.split('files/')[1]



# DB 초기화에 대비한 db add 부분. 지울 것
@app.route('/init', methods=["GET"])
def init_pair():
    people = People('KyungJoo', 'rudwn826@naver.com', '1234')
    db.session.add(people)
    db.session.commit()

    return redirect(url_for("/dashboard"))
