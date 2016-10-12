# -*- coding:utf-8 -*-

import re
from abc import ABCMeta, abstractmethod

'''
def deleteLineFeed():
    global str
    str = re.sub('\n+', '\n', str)
'''


class Hi:
    originFile = ''
    compFile = ''
    originToken = []
    compToken = []

    def __init__(self, originFile, compFile):
        self.originFile = originFile
        self.compFile = compFile

    def deleteComment(self, start, end):
        filter = Filter(self.originFile)
        self.originFile = filter.deleteComment(start, end)

        filter.setFile(self.compFile)
        self.compFile = filter.deleteComment(start, end)

        del filter

        return '주석 제거 완료'

    def listing(self):
        filter = Filter(self.originFile)
        self.originFile = filter.listing()

        filter.setFile(self.compFile)
        self.compFile = filter.listing()

        del filter

        return '리스트화 완료'

    def tokenizing(self):
        filter = Filter(self.originFile)
        del self.originToken[:]
        self.originToken.extend(filter.tokenizing())

        filter.setFile(self.compFile)
        del self.compToken[:]
        self.compToken.extend(filter.tokenizing())

        del filter

        return '토큰화 완료'

    def calcSimilarity(self, method):
        # 순서없는 검사일 경우 mapping() 호출이후 유사도 계산하여 리턴
        # 순서있는 검사일 경우 바로 LCS 알고리즘 수행

        resList = method.calcSimilarity()

        return [resList[0], float(resList[1])/len(self.originFile)*100]


class Filter:
    file = ''

    def __init__(self, file):
        self.file = file

    def setFile(self, file):
        self.file = file

    def listing(self):
        return self.file.split('\n')

    def deleteComment(self, start, end):
        while (1):
            startIdx = self.file.find(start)
            if (startIdx == -1):
                break

            endIdx = self.file[startIdx:].find(end)
            if (endIdx == -1):
                # endIdx = len(str) - startIdx
                self.file = self.file[:startIdx]

                break

            # 라인피드는 놔두고, */ 문자열은 지워야 함
            _range = 0 if end == '\n' else 2

            retStr = self.file[:startIdx] + self.file[startIdx + endIdx + _range:]
            self.file = retStr

        return self.file

    def tokenizing(self):
        stopWords = ['', ' ', '{', '}']
        retList = []

        for i in range(len(self.file)):
            self.file[i] = self.file[i].replace('\t', '')
            list = self.file[i].split(' ')

            for j in range(len(list)):
                if list[j] in stopWords:
                    list.pop(j)

            if list != []:
                retList.append(list)

        return retList

    def mapping(self):
        mappedList = []

        for i in range(len(self.file)):
            dict = {}
            for token in self.file[i]:
                if dict.get(token, 0) == 0:
                    dict[token] = 1
                else:
                    dict[token] += 1
            mappedList.append(dict)

        return mappedList


'''
유사도 검출 클래스
'''


class Check:
    __metaclass__ = ABCMeta

    originToken = []
    compToken = []

    def __init__(self, origin, comp):
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
