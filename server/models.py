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
    pNum = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pName = db.Column(db.String(50), unique=True, nullable=False)
    pEmail = db.Column(db.String(50), nullable=False)
    pPw = db.Column(db.String(255), nullable=True, default='None')
    pAuth = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, pName, pEmail, pPw=None, pAuth=False):
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
    projNum = db.Column(db.Integer, primary_key=True, autoincrement=True)
    projName = db.Column(db.String(50), nullable=False, unique=True)
    pNum = db.Column(db.String(50), nullable=False)
    fileNum = db.Column(db.String(255), nullable=True, default=None)
    date = db.Column(db.TIMESTAMP, default=datetime.now)
    update = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    def __init__(self, projName, pNum, fileNum=None):
        self.projName = projName
        self.fileNum = fileNum
        self.pNum = pNum

    def __repr__(self):
        return '<Project %r>' % self.projName


class File(db.Model):
    __tablename__ = 'file_tbl'
    fileNum = db.Column(db.Integer, primary_key=True, autoincrement=True)
    originPath = db.Column(db.String(255), nullable=False)
    compPath = db.Column(db.String(255), nullable=False)

    def __init__(self, originPath, compPath):
        self.originPath = originPath
        self.compPath = compPath
        
    def __repr__(self):
        return '<File %r>' % self.fileNum


class Result(db.Model):
    '''
    '''
    __tablename__ = 'result_tbl'
    resultNum = db.Column(db.Integer, primary_key=True, autoincrement=True)
    originFile = db.Column(db.String(255), nullable=False)
    compFile = db.Column(db.String(255), nullable=False)
    similarity = db.Column(db.String(50), nullable=False)
    projNum = db.Column(db.Integer, nullable=False)

    def __init__(self, originFile, compFile, similarity, projNum):
        self.originFile = originFile
        self.compFile = compFile
        self.similarity = similarity
        self.projNum = projNum

    def __repr__(self):
        return '<Result %r>' % self.projNum
