from flask import Flask, request, render_template

app = Flask(__name__, static_folder='static', static_url_path='')


@app.route('/result', methods=["GET"])
def result():
    result = []
    result.append(["SearchActivity.java", "ExploreActivity.java", 89.12, ""])
    result.append(["hello.java", "world.java", 80.07, "2016-10-17"])
    result.append(["helloWorld.c", "Byeworld.c", 89.12, ""])
    result.append(["MainActivity.java", "MainActivity.java", 89.12, ""])
    result.append(["MainFragment.java", "MainFragment.java", 85.45, "2016-05-12"])
    result.append(["result.py", "Result.py", 89.12, ""])
    result.append(["hello.java", "world.java", 45.07, "2016-10-17"])
    result.append(["helloWorld.c", "Byeworld.c", 89.12, ""])
    result.append(["MainActivity.java", "MainActivity.java", 89.12, ""])
    result.append(["MainFragment.java", "MainFragment.java", 85.45, "2016-05-12"])
    result.append(["Register.js", "Register.js", 77.77, ""])
    result.append(["hello.java", "world.java", 34.45, "2016-10-17"])
    result.append(["helloWorld.c", "Byeworld.c", 89.12, ""])
    result.append(["MainActivity.java", "MainActivity.java", 89.12, ""])
    result.append(["main.c", "main.c", 85.45, "2016-05-12"])
    result.append(["DetailActivity.java", "ResultActivity.java", 89.12, ""])
    result.append(["hello.java", "world.java", 80.07, "2016-10-17"])
    result.append(["helloWorld.c", "Byeworld.c", 89.12, ""])
    result.append(["MainActivity.java", "MainActivity.java", 89.12, ""])
    result.append(["MainFragment.java", "MainFragment.java", 85.45, "2016-05-12"])

    return render_template("result.html", result = result, count = len(result))


@app.route('/result/<projectid>/<pairid>', methods=["GET"])
def detail(projectid, pairid):

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
    return render_template("detail.html", origin = originList, compare = compareList, lineCount = len(originList), sameCount = sameLineCount, similarCount = similarLineCount, list = result)


@app.route('/post', methods=["POST"])
def post():
    return request.form.get("data", "1", int)


app.run(debug=True, host='0.0.0.0', port=8888)
