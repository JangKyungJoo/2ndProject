# -*- coding:utf-8 -*-

import re
import os
from abc import ABCMeta, abstractmethod


'''
유사도 검출 클래스
'''


class Check:
    __metaclass__ = ABCMeta

    originToken = []
    compToken = []

    def setInput(self, origin, comp):
        self.originToken = origin
        self.compToken = comp

    @abstractmethod
    def calcSimilarity(self):
        pass


class OrderedCheck(Check):
    def LCS(self, origin, comp):
        dp = [[0 for col in range(len(comp) + 1)] for row in range(len(origin) + 1)]

        for i in range(1, len(dp)):
            for j in range(1, len(dp[0])):
                if origin[i - 1] == comp[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = dp[i - 1][j] if dp[i - 1][j] > dp[i][j - 1] else dp[i][j - 1]

        return float(dp[len(origin)][len(comp)]) / len(origin) * 100

    def calcSimilarity(self):
        dic = {}

        for i in range(len(self.originToken)):
            for j in range(len(self.compToken)):
                per = self.LCS(self.originToken[i], self.compToken[j])
                if per >= 70:
                    dic[i] = dic.get(i, [])
                    dic[i].append(j)

        return dic, len(dic.keys())


class UnorderedCheck(Check):
    def mapping(self, data):
        mappedList = []

        for i in range(len(data)):
            dict = {}
            for token in data[i]:
                if dict.get(token, 0) == 0:
                    dict[token] = 1
                else:
                    dict[token] += 1
            mappedList.append(dict)

        return mappedList

    def check(self, origin, comp):
        tokenList = origin.keys()

        sum = 0.0
        originTokenCount = 0
        for token in tokenList:
            originCount = origin.get(token, 0)
            compCount = comp.get(token, 0)
            sum += originCount if compCount > originCount else compCount
            originTokenCount += originCount

        return (sum / originTokenCount) * 100

    def calcSimilarity(self):
        originDictList = self.mapping(self.originToken)
        compDictList = self.mapping(self.compToken)

        dic = {}

        for i in range(len(originDictList)):
            for j in range(len(compDictList)):
                per = self.check(originDictList[i], compDictList[j])
                if per >= 70:
                    dic[i] = dic.get(i, [])
                    dic[i].append(j)

        return dic, len(dic.keys())


class PreProcessor:
    file = ''
    lineNumList = []

    def __init__(self):
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

    def setInput(self, file):
        self.file = file[0]
        self.token = file[1]

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
            _range = 0 if end == '\n' else 2

            retStr = self.file[:startIdx] + self.file[startIdx + endIdx + _range:]
            self.file = retStr

        retList = []
        plus = 0
        for i in range(len(self.file.split('\n'))):
            while i + plus in lineList:
                plus += 1
            retList.append(i + plus)

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

            list = self.file[i].split(' ')

            j = 0
            while j < len(list):
                if list[j] in stopWords:
                    list.pop(j)
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


class Compare:
    originToken = []
    compToken = []
    method = ''

    def __init__(self, method):
        self.method = method

    def setInput(self, originFile, compFile):
        self.originToken = originFile
        self.compToken = compFile

        self.method.setInput(originFile, compFile)

    def process(self):
        resList = self.method.calcSimilarity()
        print resList
        print len(self.originToken)

        return [resList[0], float(resList[1]) / len(self.originToken) * 100]

