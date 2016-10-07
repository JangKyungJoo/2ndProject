# -*- coding:utf-8 -*-

import re

str = "int a fowkds fpkw //fekowfkwfekows q fkeo\nfkeowf\n\n\n/*fpwksdfekos*/"

'''
def deleteLineFeed():
    global str
    str = re.sub('\n+', '\n', str)
'''


def deleteCaption(start, end):
    global str

    while(1):
        startIdx = str.find(start)
        if(startIdx == -1):
            break

        endIdx = str[startIdx:].find(end)
        if(endIdx == -1):
            # endIdx = len(str) - startIdx
            str = str[:startIdx]

            break

        # 라인피드는 놔두고, */ 문자열은 지워야 함
        _range = 0 if end == '\n' else 2

        retStr = str[:startIdx]+str[startIdx + endIdx + _range:]
        str = retStr

    return str


arr = [deleteCaption]

print arr[0]('//', '\n')