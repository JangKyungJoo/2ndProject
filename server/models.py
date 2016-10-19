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
    __tablename__ = 'people_tbl'
    pID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pName = db.Column(db.String(50), unique=True, nullable=False)
    pEmail = db.Column(db.String(50), nullable=False)
    pPw = db.Column(db.String(255), nullable=True, default='None')
    pAuth = db.Column(db.String(255), nullable=False, default="0")

    def __init__(self, pName, pEmail, pPw=None, pAuth="0"):
        self.pName = pName
        self.pEmail = pEmail
        if pPw is None:
            self.pPw = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20))
        else:
            self.pPw = pwd_context.encrypt(pPw)
        self.pAuth = pAuth

    def verify_password(self, password):
        return pwd_context.verify(password, self.pPw)

    def change_password(self, password):
        self.pPw = pwd_context.encrypt(password)
        return True
        
    def __repr__(self):
        return '<People %r>' % self.pEmail

        
class Project(db.Model):
    '''
    '''
    __tablename__ = 'project_tbl'
    projID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    projName = db.Column(db.String(50), nullable=False, unique=True)
    projDesc = db.Column(db.String(255), nullable=True)
    pID = db.Column(db.String(50), nullable=False)
    fileNum = db.Column(db.String(255), nullable=True, default=None)
    date = db.Column(db.TIMESTAMP, default=datetime.now)
    update = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    def __init__(self, projName, projDesc, pID, fileNum=None):
        self.projName = projName
        self.projDesc = projDesc
        self.fileNum = fileNum
        self.pID = pID

    def __repr__(self):
        return '<Project %r>' % self.projName


class File(db.Model):
    __tablename__ = 'file_tbl'
    fileID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    originPath = db.Column(db.String(255), nullable=False)
    compPath = db.Column(db.String(255), nullable=False)

    def __init__(self, originPath, compPath):
        self.originPath = originPath
        self.compPath = compPath
        
    def __repr__(self):
        return '<File %r>' % self.fileID


class Result(db.Model):
    '''
    '''
    __tablename__ = 'result_tbl'
    resultID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pairID = db.Column(db.Integer, primary_key=True, nullable=False)
    originLine = db.Column(db.Integer, nullable=False)
    compLine = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False, default=1)
    rType = db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, pairID, originLine, compLine, count=1, rType=1):
        self.pairID = pairID
        self.originLine = originLine
        self.compLine = compLine
        self.count = count
        self.rType = rType
        
    def __repr__(self):
        return '<Result %r>' % self.resultID


class Origin(db.Model):
    __tablename__ = 'origin_tbl'
    originID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    originName = db.Column(db.String(255), nullable=False)
    originPath = db.Column(db.String(255), nullable=False)
    lineNum = db.Column(db.Integer, nullable=False)
    projID = db.Column(db.Integer, primary_key=True, nullable=False)

    def __init__(self, originID, originName, originPath, lineNum, projID):
        self.originID = originID
        self.originName = originName
        self.originPath = originPath
        self.lineNum = lineNum
        self.projID = projID

    def __repr__(self):
        return '<Origin %r>' % self.originID


class Compare(db.Model):
    __tablename__ = 'compare_tbl'
    compID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    compName = db.Column(db.String(255), nullable=False)
    compPath = db.Column(db.String(255), nullable=False)
    lineNum = db.Column(db.Integer, nullable=False)
    projID = db.Column(db.Integer, primary_key=True, nullable=False)

    def __init__(self, compID, compName, compPath, lineNum, projID):
        self.compID = compID
        self.compName = compName
        self.compPath = compPath
        self.lineNum = lineNum
        self.projID = projID

    def __repr__(self):
        return '<Compare %r>' % self.compID


class Pair(db.Model):
    __tablename__ = 'pair_tbl'
    pairID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    originID = db.Column(db.Integer, nullable=False)
    compID = db.Column(db.Integer, nullable=False)
    projID = db.Column(db.Integer, nullable=False)

    def __init__(self, originID, compID, projID):
        self.originID = originID
        self.compID = compID
        self.projID = projID

    def __repr__(self):
        return '<Pair %r>' % self.pairID
