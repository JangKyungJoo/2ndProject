#-*- coding: utf-8 -*-
from flask import Flask, request, render_template
from flask import url_for
from werkzeug.utils import secure_filename, redirect
from server import app
import os



# app = Flask(__name__, static_folder='static', static_url_path='')
UPLOAD_FOLDER = "/Users/kyungjoo/Downloads/test"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'pptx', 'zip'])

def readFirst():
    f = open("/Users/kyungjoo/Documents/Document/Maestro-backend/maestro/routes/board.js", 'r')
    lines = f.readlines()
    result = []
    for line in lines:
        result.append(line)
    f.close()
    return result


def readSecond():
    f = open("/Users/kyungjoo/Documents/Document/Maestro-backend/maestro/routes/anonymity.js", 'r')
    lines = f.readlines()
    result = []
    for line in lines:
        result.append(line)
    f.close()
    return result

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=["GET"])
def upload():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("upload.html", files = files)

@app.route('/upload/submit', methods=["POST"])
def submit():
    file = request.files['files']
    if file:
        filename = secure_filename(file.filename)
        if allowed_file(filename):
            path = UPLOAD_FOLDER + "/" + filename
            file.save(path)
        return redirect(url_for('upload'))

"""
@app.route('/result/{projectid}/{pairid}', methods=["GET"])
def result():
    return render_template()
"""

@app.route('/result', methods=["GET"])
def home():
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
    result = []         # 원본라인 / 비교본라인 / 유형(동일, 유사)

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
                        elif result[len(result)-1][0] == originlineNum:
                            result[len(result)-1] = [originlineNum, comparelineNum, SAME]
                        else:
                            result.append([originlineNum, comparelineNum, SAME])
                            sameLineCount+=1

                    # 유사
                    elif tokenCount > 2 and (tokenCount / len(oword)) > 0.3 :
                        print ('similar : %d, %d' %(originlineNum, comparelineNum))
                        if len(result) == 0:
                            result.append([originlineNum, comparelineNum, SIMILAR])
                            similarLineCount += 1
                        elif result[len(result)-1][0] == originlineNum:
                            if tokenCount / len(oword) > tempPercent:
                                result[len(result)-1] = [originlineNum, comparelineNum, SIMILAR]
                        else:
                            result.append([originlineNum, comparelineNum, SIMILAR])
                            similarLineCount+=1

                comparelineNum += 1
            comparelineNum = 1
            tempPercent = 0
        originlineNum += 1

    # 비교본의 라인으로 오름차순 list
    #compare = sorted(result, key=lambda x: x[1])

    # 원본소스코드 / 비교본 소스코드 / 원본 총 라인수 / 동일 라인수 / 유사 라인수 / 원본 기준 결과 / 비교본 기준 결과
    return render_template("result.html", origin = originList, compare = compareList, lineCount = len(originList), sameCount = sameLineCount, similarCount = similarLineCount, list = result)


@app.route('/post', methods=["POST"])
def post():
    return request.form.get("data", "1", int)
