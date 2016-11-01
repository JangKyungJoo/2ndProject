# -*- coding: utf-8 -*-

from server import app
from server import db
from flask import render_template
from flask import request, redirect, url_for, jsonify
from flask import session
from server.models import Pair
from server.models import Result
from server.models import Origin
from server.models import Compare
from server.models import Project
from server.models import File
from multiprocessing import Process, Queue
import time
import datetime

import filter
import sys, os
import views

process_dict = {}


@app.route('/compare', methods=["GET"])
def comparePageOpen():
    projectId = getProjectId()

    db.session.query(Project).filter(Project.projID == projectId).update(
        dict(update=datetime.datetime.now(), lastPair=0, compareMethod=0))
    db.session.commit()
    project = db.session.query(Project).filter(Project.projID == projectId).first()

    print project.lastPair

    return render_template("submit.html", projectId=projectId, lastPair=project.lastPair,
                           compareMethod=project.compareMethod)


@app.route('/compare', methods=["POST"])
def compare():
    lastPair = request.form.get('lastPair')
    compareMethod = request.form.get('compareMethod')

    projectId = getProjectId()

    q = Queue()
    pr = Process(target=compareWithProcesses, args=(projectId, q, int(lastPair), int(compareMethod)))
    pr.daemon = True
    pr.start()

    process_dict[projectId] = [pr, q]

    numOfPair = len(db.session.query(Pair).filter(Pair.projID == projectId).all())
    return jsonify(numOfPair)
    # return render_template("compare.html", projectid=projectid)


def compareWithProcesses(projectId, q, lastPair, compareMethod):
    # 프로젝트 내에 있는 비교쌍들을 불러온다.
    # 비교쌍 리스트 갯수만큼 filter를 돌림.

    "/Users/user/PycharmProjects/filter_flask/ex/origin/4340897.c"
    "/Users/user/PycharmProjects/filter_flask/ex/compare/4370143.c"

    db.session.query(Pair).delete()
    db.session.query(Result).delete()
    db.session.query(Origin).delete()
    db.session.query(Compare).delete()

    p1 = Pair(1, 1, projectId)
    p2 = Pair(1, 2, projectId)
    p3 = Pair(2, 1, projectId)
    p4 = Pair(2, 2, projectId)

    o1 = Origin("4340897.c", "/Users/user/PycharmProjects/filter_flask/ex/origin", 123, projectId)
    o2 = Origin("1009.cpp", "/Users/user/Desktop/multi/baekjoon-master/CPP14", 123, projectId)
    c1 = Compare("4370143.c", "/Users/user/PycharmProjects/filter_flask/ex/compare", 123, projectId)
    c2 = Compare("1100.cpp", "/Users/user/Desktop/multi/baekjoon-master/CPP14", 123, projectId)

    db.session.add(o1)
    db.session.add(o2)
    db.session.add(c1)
    db.session.add(c2)

    db.session.add(p1)
    db.session.add(p2)
    db.session.add(p3)
    db.session.add(p4)
    db.session.query(Project).filter(Project.projID == projectId).update(
        dict(compareMethod=compareMethod))

    db.session.commit()

    stage = lastPair
    # print '스테이지 : '+str(stage)

    for pair in db.session.query(Pair).filter(Pair.projID == projectId, lastPair < Pair.pairID):
        originFile = db.session.query(Origin).filter(Origin.originID == pair.originID).first()
        origin = originFile.originPath + '/' + originFile.originName

        compFile = db.session.query(Compare).filter(Compare.compID == pair.compID).first()
        comp = compFile.compPath + '/' + compFile.compName

        filter.compareOnePair(origin, comp, pair.pairID, compareMethod)
        db.session.query(Project).filter(Project.projID == projectId).update(
            dict(lastPair=pair.pairID))
        db.session.commit()

        q.put(pair.pairID)
        # print "put : " + str(pair.pairID)
    db.session.query(Project).filter(Project.projID == projectId).update(
        dict(lastPair=0))
    db.session.commit()


@app.route("/compare/state", methods=["GET"])
def processState():
    projectId = getProjectId()

    process_set = process_dict.get(projectId, -1)
    if process_set == -1:
        return -1
    q = process_set[1]

    currentNumber = -1

    while True:
        try:
            currentNumber = q.get(block=False)
        except:
            break

    # print currentNumber
    return jsonify(currentNumber)


@app.route("/compare/cancel", methods=["POST"])
def cancelCompare():
    projectId = getProjectId()

    pr = process_dict[projectId][0]
    print pr, pr.is_alive()
    pr.terminate()

    del (process_dict[projectId])

    return redirect('/dashboard')


def getProjectId():
    if not session['project'] or session['project'] == "":
        return redirect(url_for('dashboard'))
    else:
        projName = session['project']

    project = db.session.query(Project).filter(Project.projName == projName).first()
    projectId = project.projID

    return projectId