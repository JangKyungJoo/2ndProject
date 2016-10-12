# -*- coding: utf-8 -*-
import os
import datetime
import urlparse

from flask import Flask, render_template, request, redirect, url_for, make_response, send_file, jsonify

app = Flask(__name__)

dirName = u'/Users/user/Desktop/posting/'
elementNumber = 12

file_names = os.listdir(dirName)


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    pages = get_page_list(1)
    print pages

    return render_template('ex.html', file_names=file_names[0:12],
                           end=len(file_names[0:12]), page_num=1, page_list_num=1, pages=pages)


@app.route('/file', methods=['POST'])
def file_upload():
    global file_names

    f = request.files['file']
    print f.filename
    f.save(dirName + f.filename)

    # 업데이트 시점 생각하기
    file_names = os.listdir(dirName)

    return 'file uploaded successfully'


# URL 액션 필요없음
@app.route('/file/<file_name>', methods=['GET'])
def get_file_info(file_name):
    return send_file((dirName + file_name).encode('utf-8'), as_attachment=True)



# 페이지네이션 부분 함수화
@app.route('/page/<list_num>/<num>', methods=['GET'])
def page_move(list_num, num):
    files = file_names[((int(num) - 1) * elementNumber):(int(num) * elementNumber)]
    pages = get_page_list(int(list_num))

    print pages
    
    return render_template('ex.html', file_names=files,
                           end=len(files), page_num=num, page_list_num=list_num, pages=pages)



#파일 이름, 파일 크기, 변경된 날짜, 종류
@app.route('/file/property/<file_name>', methods=['GET'])
def file_property(file_name):
    size = os.path.getsize(dirName+file_name)
    ctime = datetime.datetime.fromtimestamp(os.path.getmtime(dirName+file_name))
    list = [file_name, size, ctime, file_name.rsplit('.')[1]]

    return jsonify(list=list)


# 액션 지우고 메서드만으로 구분
@app.route('/file/<file_name>', methods=['DELETE'])
def file_deletion(file_name):
    global file_names

    os.remove(dirName+file_name)
    file_names = os.listdir(dirName)

    return hello_world()

def get_page_list(page_list_num):
    all_pages = (len(file_names) - 1) / elementNumber + 1
    end_page = page_list_num * 10 if ((all_pages - 1) / (page_list_num * 10)) > 0 else all_pages

    return range(page_list_num * 10 - 9, end_page + 1)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
