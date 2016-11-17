#-*- coding: utf-8 -*-
import os

from flask import Flask, request, render_template
from flask import redirect
from flask import send_file
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
import csv

from server.views import login_required


@app.route('/result', methods=["GET"])
@login_required
def default():
    if not session['projID'] or session['projID'] == "":
        return redirect(url_for('dashboard'))
    else:
        projID = session['projID']
        return redirect('result/' + str(projID))


@app.route('/result/<projectid>', methods=["GET"])
@login_required
def result(projectid):

    project = Project.query.get(projectid)

    if project.fileNum is None:
        return redirect(url_for('file_upload'))

    projName = project.projName

    pair = Pair.query.filter(Pair.projID == projectid).order_by(Pair.similarity.desc()).all()

    origin_list = Origin.query.filter(Origin.projID == projectid).order_by(Origin.originID).all()
    origin_flag = origin_list[0].originID
    compare_list = Compare.query.filter(Compare.projID == projectid).order_by(Compare.compID).all()
    compare_flag = compare_list[0].compID

    json_list = []
    for item in pair:
        origin_range = item.originID - origin_flag
        compare_range = item.compID - compare_flag
        if origin_range >= 0 and origin_range < len(origin_list) and compare_range >=0 and compare_range < len(compare_list):
            json_list.append(Pair.serialize(item, origin_list[origin_range].originName, compare_list[compare_range].compName))


    pair = Pair.query.filter(Pair.projID == projectid).order_by(Pair.similarity.desc(), Pair.modifyDate.desc()).all()
    json_list2 = []
    for item in pair:
        origin_range = item.originID - origin_flag
        compare_range = item.compID - compare_flag
        if origin_range >= 0 and origin_range < len(origin_list) and compare_range >=0 and compare_range < len(compare_list):
            json_list2.append(Pair.serialize(item, origin_list[origin_range].originName, compare_list[compare_range].compName))

    return render_template("result.html", dateByAsc=json.dumps(json_list), dateByDesc=json.dumps(json_list2), pairCount=len(pair), projectid=projectid, projName = projName)


@app.route('/result/<projectid>/<pairid>', methods=["GET", "POST"])
@login_required
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
        cnt = 0
        for line in lines:
            if len(line) > 2:
                cnt+=1
            originList.append(line)

        lines = compFile.readlines()
        for line in lines:
            compareList.append(line)

        result = Result.query.filter(Result.pairID == pairid).order_by(Result.originLine).all()
        list = [i.serialize for i in result]

        # 원본소스코드 / 비교본 소스코드 / 원본 기준 결과
        return render_template("detail.html", origin=originList, originCount=cnt, compare=compareList, list=json.dumps(list), pairid = pairid, originPath = getPath(originPath), compPath = getPath(comparePath))

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
        lineNum = origin.lineNum
        count = Result.query.filter(Result.pairID == pair.pairID).count()

        pair.similarity = count * 100.0 / lineNum
        pair.modifyDate = datetime.now()
        db.session.add(pair)
        db.session.commit()

        return render_template("detail.html")


@app.route('/result/<projectid>/save', methods=["GET"])
@login_required
def save(projectid):
    projID = projectid
    projName = Project.query.get(projID).projName
    result = []
    origin = ['', 'origin file']
    compare = ['', 'compare file']
    similarity = ['project : ', 'similarity (%)']
    modify = [projName, 'modify date']

    pair = Pair.query.filter(Pair.projID == projectid).order_by(Pair.similarity.desc()).all()
    origin_list = Origin.query.filter(Origin.projID == projectid).order_by(Origin.originID).all()
    origin_flag = origin_list[0].originID
    compare_list = Compare.query.filter(Compare.projID == projectid).order_by(Compare.compID).all()
    compare_flag = compare_list[0].compID

    for item in pair:
        origin_range = item.originID - origin_flag
        compare_range = item.compID - compare_flag
        if origin_range >= 0 and origin_range < len(origin_list) and compare_range >=0 and compare_range < len(compare_list):
            origin.append(origin_list[origin_range].originName)
            compare.append(compare_list[compare_range].compName)
            similarity.append(format(item.similarity, '.2f'))
            modify.append(str(item.modifyDate.strftime("%Y-%m-%d %H:%M")))

    result.append(origin)
    result.append(compare)
    result.append(similarity)
    result.append(modify)

    length = Pair.query.filter(Pair.projID == projectid).count()
    path = os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], projID), 'result.csv')

    with codecs.open(path, 'wb', encoding = 'utf-8') as file:
        csv_writer = csv.writer(file)
        for y in range(length):
            csv_writer.writerow([x[y].encode('utf-8') for x in result])

    return send_file(path,
                     mimetype='text/csv',
                     attachment_filename='result.csv',
                     as_attachment=True)


def getPath(path):
    temp = path[len(app.config['UPLOAD_FOLDER']):]
    return temp.split('files/')[1]