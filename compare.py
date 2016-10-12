# -*- coding:utf-8 -*-
import os

originSourcePath = os.getcwd()+'/ex/4370143.c'
compSourcePath = os.getcwd()+'/ex/4340897.c'


# 소스 코드를 읽어서 개행문자 단위로 리스팅
def readSource(path):
    f = open(path, 'r')
    data = f.read()
    splitData = data.split('\n')

    return splitData


# 공백 단위로 토큰화
def tokenizing(data):
    stopWords = ['', ' ', '{', '}']
    retList = []

    for i in range(len(data)):
        data[i] = data[i].replace('\t', '')
        list = data[i].split(' ')

        for j in range(len(list)):
            if list[j] in stopWords:
                list.pop(j)

        if list != []:
            retList.append(list)

    return retList


# 토큰을 딕셔너리에 매핑
def mapping(data):
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


def calcSimilarity(origin, comp, originTokenLength):
    tokenList = origin.keys()

    sum = 0.0
    for token in tokenList:
        originCount = origin.get(token, 0)
        compCount = comp.get(token, 0)
        sum += originCount if compCount > originCount else compCount

    return (sum / originTokenLength) * 100

'''
def min(x, y):
    return x if x < y else y


def editDistance(origin, comp):
    dp = [[0 for col in range(len(comp)+1)] for row in range(len(origin)+1)]

    for i in range(len(dp)):
        dp[i][0] = i
    for j in range(len(dp[0])):
        dp[0][j] = j

    for i in range(1, len(dp)):
        for j in range(1, len(dp[0])):
            if origin[i-1] == comp[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j-1], min(dp[i-1][j], dp[i][j-1])) + 1

    return dp[len(origin)][len(comp)]
'''


def LCS(origin, comp):
    dp = [[0 for col in range(len(comp) + 1)] for row in range(len(origin) + 1)]

    for i in range(1, len(dp)):
        for j in range(1, len(dp[0])):
            if(origin[i-1] == comp[j-1]):
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = dp[i-1][j] if dp[i-1][j] > dp[i][j-1] else dp[i][j-1]

    return float(dp[len(origin)][len(comp)]) / len(origin) * 100


originData = readSource(originSourcePath)
compData = readSource(compSourcePath)

tokOriginData = tokenizing(originData)
tokCompData = tokenizing(compData)


# 순서 고려하지 않은 비교 (토큰을 딕셔너리에 매핑)

mappedOriginList = mapping(tokOriginData)
mappedCompList = mapping(tokCompData)

for i in range(len(mappedOriginList)):
    for j in range(len(mappedCompList)):
        per = calcSimilarity(mappedOriginList[i], mappedCompList[j], len(tokOriginData[i]))
        if per > 0:
            print i, j, per

# 순서 고려한 비교 (LCS 알고리즘)

print '\n'

for i in range(len(tokOriginData)):
    for j in range(len(tokCompData)):
        per = LCS(tokOriginData[i], tokCompData[j])
        if per > 0:
            print i, j, per
