# -*- coding: utf-8 -*-
from passlib.apps import custom_app_context as pwd_context
from server import db
from server import app
from server.cipher import Crypter
from datetime import datetime
import os
import random
import string

class People(db.Model):
    '''
        사용자 관리 테이블
    '''
    __tablename__ = 'people_tbl'
    pID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    '''사용자 번호 '''
    pName = db.Column(db.String(50), unique=True, nullable=False)
    '''사용자 이름 '''
    pEmail = db.Column(db.String(50), nullable=False)
    '''사용자 이메일 '''
    pPw = db.Column(db.String(255), nullable=True, default='None')
    '''비밀번호 '''
    pAuth = db.Column(db.String(255), nullable=False, default="0")
    '''관리자 계정 여부 '''

    def __init__(self, pName, pEmail, pPw=None, pAuth="0"):
        self.pName = pName
        self.pEmail = pEmail
        if pPw is None:
            self.pPw = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20))
        else:
            self.pPw = pwd_context.encrypt(pPw)
        self.pAuth = pAuth

    def verify_password(self, password):
        '''
            인증 루틴에 사용되는 패스워드 인증 체크 함수


            :param string password: 인증 요청 시 입력한 패스워드

        '''
        return pwd_context.verify(password, self.pPw)

    def change_password(self, password):
        '''
            패스워드 변경 함수


            :param string password: 변경하고 싶은 패스워드
        '''
        self.pPw = pwd_context.encrypt(password)
        return True
        
    def __repr__(self):
        return '<People %r>' % self.pEmail

        
class Project(db.Model):
    '''
        프로젝트 관리 테이블
    '''
    __tablename__ = 'project_tbl'
    projID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    '''프로젝트 번호 '''
    projName = db.Column(db.String(50), nullable=False, unique=True)
    '''프로젝트 이름 '''
    projDesc = db.Column(db.String(255), nullable=True)
    '''프로젝트 설명 '''
    pID = db.Column(db.String(50), db.ForeignKey('people_tbl.pID'), nullable=False)
    '''프로젝트 소유자 번호 '''
    fileNum = db.Column(db.String(255), nullable=True, default=None)
    '''프로젝트 파일 번호 '''
    date = db.Column(db.TIMESTAMP, default=datetime.now)
    '''프로젝트 생성 시각 '''
    update = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    '''프로젝트 최종 수정 시각 '''

    def __init__(self, projName, projDesc, pID, fileNum=None):
        self.projName = projName
        self.projDesc = projDesc
        self.fileNum = fileNum
        self.pID = pID

    def __repr__(self):
        return '<Project %r>' % self.projName


class File(db.Model):
    '''
        파일 관리 테이블
    '''
    __tablename__ = 'file_tbl'
    fileID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    '''파일 번호 '''
    originPath = db.Column(db.String(255), nullable=False)
    '''원본 파일 경로 '''
    compPath = db.Column(db.String(255), nullable=False)
    '''비교 파일 경로 '''

    def __init__(self, originPath, compPath):
        self.originPath = originPath
        self.compPath = compPath
        
    def __repr__(self):
        return '<File %r>' % self.fileID


class Result(db.Model):
    '''
        비교결과 관리 테이블
    '''
    __tablename__ = 'result_tbl'
    resultID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    '''비교결과 번호 '''
    pairID = db.Column(db.Integer, db.ForeignKey('pair_tbl.pairID'), nullable=False)
    '''비교쌍 번호 '''
    originLine = db.Column(db.Integer, nullable=False)
    '''원본 라인 번호 '''
    compLine = db.Column(db.Integer, nullable=False)
    '''비교 라인 번호 '''
    rType = db.Column(db.Integer, nullable=False, default=1)
    '''결과 유형

        
        :rType 1: 일치
        :rType 2: 유사
    '''

    def __init__(self, pairID, originLine, compLine, rType=1):
        self.pairID = pairID
        self.originLine = originLine
        self.compLine = compLine
        self.rType = rType
        
    def __repr__(self):
        return '<Result %r>' % self.resultID

    @property
    def serialize(self):
       return {
           'pairID' : self.pairID,
           'originLine' : self.originLine,
           'compLine' : self.compLine,
           'rType' : self.rType
       }


class Origin(db.Model):
    '''
        원본 정보 테이블
    '''
    __tablename__ = 'origin_tbl'
    originID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    '''원본 번호 '''
    originName = db.Column(db.String(255), nullable=False)
    '''원본 파일명 '''
    originPath = db.Column(db.String(255), nullable=False)
    '''원본 파일 경로 '''
    lineNum = db.Column(db.Integer, nullable=True)
    '''총 라인 수 '''
    projID = db.Column(db.Integer, db.ForeignKey('project_tbl.projID'), nullable=False)
    '''프로젝트 번호 '''

    def __init__(self, originName, originPath, lineNum, projID):
        self.originName = originName
        self.originPath = originPath
        self.lineNum = lineNum
        self.projID = projID

    def __repr__(self):
        return '<Origin %r>' % self.originID


class Compare(db.Model):
    '''
        비교본 정보 테이블
    '''
    __tablename__ = 'compare_tbl'
    compID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    '''비교본 번호 '''
    compName = db.Column(db.String(255), nullable=False)
    '''비교본 파일명 '''
    compPath = db.Column(db.String(255), nullable=False)
    '''비교본 파일 경로 '''
    lineNum = db.Column(db.Integer, nullable=False)
    '''총 라인 수 '''
    projID = db.Column(db.Integer, db.ForeignKey('project_tbl.projID'), nullable=False)
    '''프로젝트 번호 '''

    def __init__(self, compName, compPath, lineNum, projID):
        self.compName = compName
        self.compPath = compPath
        self.lineNum = lineNum
        self.projID = projID

    def __repr__(self):
        return '<Compare %r>' % self.compID


class Pair(db.Model):
    '''
        비교쌍 관리 테이블
    '''
    __tablename__ = 'pair_tbl'
    pairID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    '''비교쌍 번호 '''
    originID = db.Column(db.Integer, db.ForeignKey('origin_tbl.originID'), nullable=False)
    '''원본 번호 '''
    compID = db.Column(db.Integer, db.ForeignKey('compare_tbl.compID'), nullable=False)
    '''비교본 번호 '''
    projID = db.Column(db.Integer, db.ForeignKey('project_tbl.projID'), nullable=False)
    '''프로젝트 번호 '''
    similarity = db.Column(db.Float, default=0)
    '''유사도'''
    modifyDate = db.Column(db.TIMESTAMP, nullable=True)
    '''수정날짜'''
    
    def __init__(self, originID, compID, projID):
        self.originID = originID
        self.compID = compID
        self.projID = projID

    def __repr__(self):
        return '<Pair %r>' % self.pairID


    def serialize(self, originFile, compareFile):
       return {
           'pairID' : self.pairID,
           'originID' : self.originID,
           'originFile' : originFile,
           'compID' : self.compID,
           'compareFile' : compareFile,
           'similarity' : self.similarity,
           'modifyDate' : self.modifyDate
       }
