from flask import Flask, request, render_template
from flask import url_for
from werkzeug.utils import secure_filename, redirect
import os


app = Flask(__name__, static_folder='static', static_url_path='')
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



@app.route('/', methods=["GET"])
def home():
    origin = open("/Users/kyungjoo/Documents/Document/Maestro-backend/maestro/routes/board.js", 'r')
    compare = open("/Users/kyungjoo/Documents/Document/Maestro-backend/maestro/routes/anonymity.js", 'r')
    charToken = [',', '.', '/', ';', '*', '(', ')', '-', '_', '&', '%']
    originList = []
    compareList = []
    compareLine = [-1]    # 비교본 입장에서 오름차순으로 저장한 유사 라인 정보
    lines = origin.readlines()
    for line in lines:
        originList.append(line)
    lines = compare.readlines()
    for line in lines:
        compareLine.append(-1)
        compareList.append(line)

    lineCount = 0
    originlineNum = 1
    comparelineNum = 1
    similarLine = [-1]    # 원본 입장에서 오름차순으로 저장한 유사 라인 정보
    tempPercent = 0
    for oline in originList:
        similarLine.append(-1)
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
                    if tokenCount > 2 and (tokenCount / len(oword)) > 0.3 :
                        print ('similar : %d, %d' %(originlineNum, comparelineNum))
                        if similarLine[originlineNum] == -1:
                            similarLine[originlineNum] = comparelineNum
                            tempPercent = tokenCount / len(oword)
                            lineCount += 1
                        else:
                            if tokenCount / len(oword) > tempPercent:
                                similarLine[originlineNum] = comparelineNum
                                tempPercent = tokenCount / len(oword)
                    elif tokenCount == 2 and tokenCount / len(oword) == 1:
                        print('similar : %d, %d' % (originlineNum, comparelineNum))
                        if similarLine[originlineNum] == -1:
                            similarLine[originlineNum] = comparelineNum
                            tempPercent = tokenCount / len(oword)
                            lineCount += 1
                        else:
                            if tokenCount / len(oword) > tempPercent:
                                similarLine[originlineNum] = comparelineNum
                                tempPercent = tokenCount / len(oword)
                comparelineNum += 1
            comparelineNum = 1
            tempPercent = 0
        originlineNum += 1

    # similarLine으로부터 compareLine 생성
    cnt = 1
    for line in similarLine:
        if line!=-1:
            compareLine[line] = cnt
        cnt+=1

    return render_template("result.html", origin = originList, compare = compareList, lineCount = lineCount, list = similarLine, list2 = compareLine)


@app.route('/post', methods=["POST"])
def post():
    return request.form.get("data", "1", int)


app.run(debug=True, host='0.0.0.0', port=8888)
