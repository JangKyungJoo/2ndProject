# -*- coding:utf-8 -*-

import re
from abc import ABCMeta, abstractmethod
import lexer.clexer as clexer


class PreProcessor:
    file = ''
    lineNumList = []

    def __init__(self, **kwargs):
        pass

    def setInput(self, file):
        pass

    def setLineNumInfo(self, lineNumList):
        pass

    def process(self):
        pass


class RemoveBlank(PreProcessor):
    def setInput(self, file):
        self.file = file.split('\n')

    def setLineNumInfo(self, lineNumList):
        self.lineNumList = lineNumList

    def process(self):
        blankList = []

        for i in range(len(self.file)):
            self.file[i] = re.sub('\t+', '', self.file[i])
            self.file[i] = re.sub(' +', ' ', self.file[i])
            if self.file[i] == '' or self.file[i] == '\t' or self.file[i] == ' ':
                blankList.append(i)

        ele = 0
        while ele < len(self.file):
            if self.file[ele] == '' or self.file[ele] == '\t' or self.file[ele] == ' ':
                self.file.pop(ele)
                ele -= 1
            ele += 1

        retList = []
        plus = 0

        for i in range(len(self.file)):
            # print i+1, str[i]
            while i + plus in blankList:
                plus += 1
            retList.append(self.lineNumList[i + plus])

            # for i in range(len(retList)):
            # print i+1, '-', retList[i]+1

        return self.file, retList


class RemoveComment(PreProcessor):
    token = []

    def __init__(self, **kwargs):
        self.token = kwargs.get('token', [])

    def setInput(self, file):
        # 파일만 받아오도록
        self.file = file

    def setLineNumInfo(self, lineNumList):
        self.lineNumList = lineNumList

    def process(self):
        lineList = []
        lineNum = 0

        start = self.token[0]
        end = self.token[1]

        while 1:
            startIdx = self.file.find(start)
            if startIdx == -1:
                break

            endIdx = self.file[startIdx:].find(end)
            if endIdx == -1:
                # endIdx = len(str) - startIdx
                self.file = self.file[:startIdx]

                break

            lineCount = self.file[:startIdx].count('\n')
            for i in range(self.file[startIdx:(startIdx + endIdx)].count('\n')):
                lineList.append(self.lineNumList[lineCount + lineNum + i + 1])
            lineNum = len(lineList)

            # 라인피드는 놔두고, */ 문자열은 지워야 함
            _range = 0 if end == '\n' else len(end)

            retStr = self.file[:startIdx] + self.file[startIdx + endIdx + _range:]
            self.file = retStr

        retList = []
        plus = 0
        for i in range(len(self.file.split('\n'))):
            while i + plus in lineList:
                plus += 1
            retList.append(self.lineNumList[i + plus])

        return self.file, retList


class Tokenizing(PreProcessor):
    def setInput(self, file):
        self.file = file

    def setLineNumInfo(self, lineNumList):
        self.lineNumList = lineNumList

    def process(self):
        stopWords = ['', ' ', '{', '}']
        retList = []
        blankList = []
        lineList = []

        for i in range(len(self.file)):
            list = self.tokenize(self.file[i])
            j = 0
            while j < len(list):
                # print list[j]
                if list[j] in stopWords:
                    # print list[j] + ' 삭제'
                    list.pop(j)
                else:
                    j += 1

            if not list:
                blankList.append(i)

            retList.append(list)

        ele = 0
        while ele < len(retList):
            if not retList[ele]:
                retList.pop(ele)
                ele -= 1
            ele += 1

        plus = 0
        for i in range(len(retList)):
            # print i+1, str[i]
            while i + plus in blankList:
                plus += 1
            lineList.append(self.lineNumList[i + plus])

        return retList, lineList

    def tokenize(self, line):
        pass


class SpaceTokenizer(Tokenizing):
    def tokenize(self, line):
        return line.split(' ')


class CTokenizer(Tokenizing):
    def tokenize(self, line):
        lexer = clexer.initLexer()
        lexer.input(line)

        tokenList = []
        for token in lexer:
            tokenList.append(token.value)

        return tokenList



def numberMapping(orifile, compfile):
    dic = {}
    number = 0
    inputs = [orifile, compfile]
    outputs = []

    for input in inputs:
        retList = []
        for tokList in input:
            midList = []
            for token in tokList:
                if dic.get(token, -1) == -1:
                    dic[token] = number
                    number += 1
                midList.append(dic[token])
            retList.append(midList)
        outputs.append(retList)

    return outputs[0], outputs[1]
