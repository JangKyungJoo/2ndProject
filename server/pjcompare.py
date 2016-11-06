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

    project = db.session.query(Project).filter(Project.projID == projectId).first()
    print '마지막 중단 지점 : '+str(project.lastPair)
    
    return render_template("submit.html", projectId=projectId, lastPair=project.lastPair,
                           compareMethod=project.compareMethod)


@app.route('/compare', methods=["POST"])
def compare():
    lastPair = request.form.get('lastPair')
    compareMethod = request.form.get('compareMethod')
    commentRemove = request.form.get('commentRemove')
    tokenizer = request.form.get('tokenizer')

    print commentRemove

    projectId = getProjectId()

    q = Queue()
    pr = Process(target=compareWithProcesses, args=(projectId, q, int(lastPair), int(compareMethod),
                                                    int(commentRemove)))
    pr.daemon = True
    pr.start()

    process_dict[projectId] = [pr, q]

    numOfPair = db.session.query(Pair).filter(Pair.projID == projectId).count()
    return jsonify(numOfPair)
    # return render_template("compare.html", projectid=projectid)


def compareWithProcesses(projectId, q, lastPair, compareMethod, commentRemove):
    # 프로젝트 내에 있는 비교쌍들을 불러온다.
    # 비교쌍 리스트 갯수만큼 filter를 돌림.

    db.session.query(Project).filter(Project.projID == projectId).update(
        dict(compareMethod=compareMethod))

    if lastPair == 0:
        for pair in db.session.query(Pair).filter(Project.projID == Pair.projID).all():
            db.session.query(Result).filter(pair.pairID == Result.pairID).delete()

    db.session.commit()

    stage = 0

    for pair in db.session.query(Pair).filter(Pair.projID == projectId):
        if lastPair >= pair.pairID:
            stage += 1
            continue

        originFile = db.session.query(Origin).filter(Origin.originID == pair.originID).first()
        origin = originFile.originPath + '/' + originFile.originName

        compFile = db.session.query(Compare).filter(Compare.compID == pair.compID).first()
        comp = compFile.compPath + '/' + compFile.compName

        filter.compareOnePair(origin, comp, pair.pairID, compareMethod, commentRemove)
        db.session.query(Project).filter(Project.projID == projectId).update(
            dict(lastPair=pair.pairID))
        db.session.commit()

        # 취소 확인

        q.put(pair.pairID)
        lastPair = pair.pairID
        stage += 1
        # print "put : " + str(pair.pairID)

    q.put(stage)
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
    pr.join()

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