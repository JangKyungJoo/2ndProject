# -*- coding:utf-8 -*-
import os
import copy
from abc import ABCMeta, abstractmethod


class Check:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    # name => compare
    @abstractmethod
    def process(self, origin, comp):
        pass


class OrderedCheck(Check):

    def process(self, origin, comp):
        dp = [[0 for col in range(len(comp) + 1)] for row in range(len(origin) + 1)]

        for i in range(1, len(dp)):
            for j in range(1, len(dp[0])):
                if origin[i - 1] == comp[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = dp[i - 1][j] if dp[i - 1][j] > dp[i][j - 1] else dp[i][j - 1]

        return float(dp[len(origin)][len(comp)]) / (len(origin) if len(origin) >= len(comp) else len(comp)) * 100


class UnorderedCheck(Check):
    def mapping(self, data):
        dict = {}

        for token in data:
            if dict.get(token, 0) == 0:
                dict[token] = 1
            else:
                dict[token] += 1

        return dict

    def process(self, origin, comp):
        origin = self.mapping(origin)
        comp = self.mapping(comp)

        tokenList = origin.keys()

        sum = 0.0
        originTokenCount = 0
        for token in tokenList:
            originCount = origin.get(token, 0)
            compCount = comp.get(token, 0)
            sum += originCount if compCount > originCount else compCount
            originTokenCount += originCount

        return (sum / originTokenCount) * 100


class EditDistance(Check):
    def process(self, origin, comp):
        dp = [[0 for col in range(len(comp) + 1)] for row in range(len(origin) + 1)]
        for i in range(len(dp)):
            dp[i][0] = i
        for j in range(len(dp[0])):
            dp[0][j] = j
        for i in range(1, len(dp)):
            for j in range(1, len(dp[0])):
                if origin[i - 1] == comp[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(dp[i - 1][j - 1], min(dp[i - 1][j], dp[i][j - 1])) + 1

        return 100.0-(dp[len(origin)][len(comp)]*20)


class Compare:
    originToken = []
    compToken = []
    method = ''
    visited = {}

    def __init__(self, method):
        self.method = method
        self.visited = {}

    def setInput(self, originFile, compFile):
        self.originToken = originFile
        self.compToken = compFile
    '''
    def process(self):
        dict = {}

        for i in range(len(self.originToken)):
            for j in range(len(self.compToken)):
                per = self.method.process(self.originToken[i], self.compToken[j])
                if per == 100.0:
                    dict[i] = dict.get(i, [])
                    dict[i].append([j, 1])
                elif per >= 70.0:
                    dict[i] = dict.get(i, [])
                    dict[i].append([j, 2])

        return dict
    '''

    def process(self):
        i = 0
        matrix = {}
        while i < len(self.originToken):
            dict = {}
            j = 0
            while j < len(self.compToken):
                if self.visited.get(j, 0) == 1:
                    j += 1
                    continue
                retList = []
                per = self.method.process(self.originToken[i], self.compToken[j])
                if per == 100.0:
                    retList = self.block(i + 1, j + 1, 0)
                    retList.append(1)
                elif per >= 70.0:
                    retList = self.block(i + 1, j + 1, 0)
                    retList.append(2)
                retList.reverse()
                dict[j] = retList

                j += len(retList)
                j += 1

            idx = 0
            maxlen = 0
            for blk in dict.keys():
                if len(dict[blk]) > maxlen:
                    maxlen = len(dict[blk])
                    idx = blk
            for k in range(idx, idx+maxlen):
                matrix[i] = [k, dict[k][k-idx]]
                self.visited[k] = 1
                i += 1
            i += 1
        return matrix

    def block(self, i, j, length):
        if len(self.originToken) >= i or len(self.compToken) >= j:
            return []
        if self.visited.get(j, 0) == 1:
            return []

        per = self.method.process(self.originToken[i], self.compToken[j])

        if per == 100.0:
            retList = self.block(i + 1, j + 1, length + 1)
            retList.append(1)
        elif per >= 70.0:
            retList = self.block(i + 1, j + 1, length + 1)
            retList.append(2)
        else:
            return []

        return retList

