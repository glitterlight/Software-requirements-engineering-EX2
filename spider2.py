import requests
from bs4 import BeautifulSoup
import chardet
import sys
import traceback
import json

class Issue:
    def __init__(self, text='', labelList=None):
        self.text = text
        self.labelList = labelList

class Spider:
    def __init__(self):
        self.url = 'https://github.com/microsoft/vscode/issues?page='
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
            "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

        self.issueList = []  # 记录issue
        self.labelDict = {}  # 记录label出现次数
        self.labelmarkDict = {}  # 记录每个标签的分数
        self.classList = [{}, {}, {}, {}, {}]  # 记录最后的分类及得分

    def getHTMLText(self, page):
        try:
            r = requests.get(self.url+page, headers=self.header, timeout=30)
            print(r.status_code)
            r.raise_for_status()
            print(r.apparent_encoding)
            r.encoding = r.apparent_encoding
            return r.text
        except:
            traceback.print_exc()
            sys.exit("the url refused requests")

    def dealHTMLText(self, text):
        soup = BeautifulSoup(text, 'lxml')
        for tr in soup.find_all('div', class_='flex-auto min-width-0 p-2 pr-3 pr-md-2'):
            content = str(tr.find('a', class_='link-gray-dark v-align-middle no-underline h4 js-navigation-open').string)
            #print(f'string: {content}')
            labelTag = tr.find('span', class_='labels lh-default d-block d-md-inline')
            #print('-------------label-------------')
            tmplabelList = []
            if labelTag == None:
                #print(labelTag)
                pass
            else:
                #print(type(labelTag))
                for label in labelTag.find_all('a', class_='IssueLabel hx_IssueLabel'):
                    labelStr = str(label.string).strip()
                    #print(labelStr)
                    tmplabelList.append(labelStr)
                    if labelStr in self.labelDict:
                        self.labelDict[labelStr] += 1
                    else:
                        self.labelDict[labelStr] = 1
                        self.labelmarkDict[labelStr] = 1

            self.issueList.append(Issue(content, tmplabelList))
            #for label in self.issueList:
            #    print(label.content)
            #print('')
            #print(self.labelDict)

    def output(self):
        with open('labeltimesDict.json', 'w') as f:
            json.dump(self.labelDict, f)
        labelList = sorted(self.labelDict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        for line in labelList:
            print(line)
        tmpList = []
        for line in self.issueList:
            #print(type(line))
            tmpList.append(line.__dict__)
        tmpDict = {'issueList': tmpList}
        with open('issueList.json', 'w') as f:
            json.dump(tmpDict, f)
        with open('markDict.json', 'w') as f:
            json.dump(self.labelmarkDict, f)

    def input(self):
        tmpDict = {}
        with open('issueList.json', 'r') as f:
            tmpDict = json.load(f)
        tmpList = tmpDict['issueList']
        self.issueList.clear()
        for line in tmpList:
            tmpIssue = Issue()
            tmpIssue.__dict__ = line
            self.issueList.append(tmpIssue)

        print(len(self.issueList))

        with open('markDict.json', 'r') as f:
            self.labelmarkDict = json.load(f)
        self.set_mark()

    def set_mark(self):
        self.labelmarkDict['debug'] = 2
        self.labelmarkDict['help wanted'] = 2
        self.labelmarkDict['integrated-terminal'] = 2
        self.labelmarkDict['api'] = 2
        self.labelmarkDict['ux'] = 2
        self.labelmarkDict['notebook'] = 2
        self.labelmarkDict['debt'] = 2
        self.labelmarkDict['task'] = 2
        self.labelmarkDict['accessibility'] = 2

        self.labelmarkDict['feature-request'] = 4
        self.labelmarkDict['extensions'] = 4

        self.labelmarkDict['bug'] = 11
        self.labelmarkDict['important'] = 11

    def classify(self):
        for issue in self.issueList:
            mark = 0
            for label in issue.labelList:
                mark += self.labelmarkDict[label]
            if mark >= 16:
                self.classList[4][issue.text] = mark
            else:
                self.classList[(mark + 4) // 5][issue.text] = mark

        for line in self.classList:
            print(len(line))

        #print(classList)

    def record(self):
        with open('result.txt', 'w') as f:
            for line in reversed(self.classList):
                lineList= sorted(line.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
                for line2 in lineList:
                    try:
                        f.write(f'{line2[0]}: {line2[1]}\n')
                    except:
                        continue
                f.write('\n\n')
                f.write('-----------------------------------------------'
                        '-----------------------------------------------'
                        '-----------------------------------------\n\n\n')

    def record2(self):
        with open('result.xls', 'w') as f:
            for line in reversed(self.classList):
                lineList= sorted(line.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
                for line2 in lineList:
                    try:
                        f.write(f'{line2[0]}\t{line2[1]}\n')
                    except:
                        continue





if __name__ == "__main__":
    spider = Spider()
    #for i in range(200):
    #    print(f'page: {i+1}')
    #    text = spider.getHTMLText(str(i+1))
    #    spider.dealHTMLText(text)
    #spider.output()
    spider.input()
    spider.classify()
    #spider.record()
    spider.record2()