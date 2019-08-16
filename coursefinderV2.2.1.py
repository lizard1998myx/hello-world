from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import csv, datetime, sys


class Course():
    def __init__(self, no, table, attempt=-1):
        self.no = str(no)
        self._outline_soup = None
        self._schedule_soup = None
        self._existence = False
        self.name = ""
        self.code = ""
        self.hour = ""
        self.credit = ""
        self.property = ""
        self.term = ""
        self.week = ""
        self.schedule = ""
        self.location = ""
        self.teacher = ""
        self._attempt = attempt + 1  # 累加错误尝试次数，初始为0
        self._max_attempts = 3
        self.table = table

    def check_existence(self):
        if str(self._outline_soup.find('', {'class': 'mc-body'}).h4.get_text()) != "":
            self._existence = True
            return True
        return False

    def isexist(self):
        return self._existence

    def get_outline(self):
        url = "http://jwxk.ucas.ac.cn/course/courseplan/" + self.no
        try:
            html = urlopen(url)
        except URLError:
            return False
        except HTTPError:
            return False
        self._outline_soup = BeautifulSoup(html, "html.parser")
        return True

    def get_schedule(self):
        url = "http://jwxk.ucas.ac.cn/course/coursetime/" + self.no
        try:
            html = urlopen(url)
        except URLError:
            return False
        except HTTPError:
            return False
        self._schedule_soup = BeautifulSoup(html, "html.parser")
        return True

    def _outline_info(self, text):
        return self._outline_soup.find(text=text).find_all_previous()[1].get_text().replace(text, "")

    def _schedule_info(self, text):
        info = ""
        for tag in self._schedule_soup.find_all(text=text):
            str = tag.find_next().get_text()
            if info == "":
                info = str
            elif str != info:
                info = info + "|" + str
        return info

    def get_info(self):
        self.name = self._outline_soup.find('', {'class': 'mc-body'}).h4.get_text()
        self.code = self._outline_info("课程编码：")
        self.hour = self._outline_info("课时：")
        self.credit = self._outline_info("学分：")
        self.property = self._outline_info("课程属性：")
        self.teacher = self._outline_info("主讲教师：")
        self.term = self._schedule_soup.find('', {'class': 'mc-body'}).find_all_next()[1].get_text().replace("：","")
        self.week = self._schedule_info("上课周次")
        self.schedule = self._schedule_info("上课时间")
        self.location = self._schedule_info("上课地点")

    def rearrange(self):  # 优化输出结果，例如开课周信息
        if self.week == "":
            return
        new_week = ""
        new_week_list = []
        for week in self.week.split("|"):
            new_string = ""
            start = -1
            last = -1
            for n in week.split("、"):
                n = int(n)
                if start==-1:
                    start = n
                elif n!=last+1:
                    if new_string != "":
                        new_string += ", "
                    new_string += str(start) + "-" + str(last)
                last = n
            new_week_list.append(new_string)
        for new_string in new_week_list:
            if new_week != "":
                new_week += "|"
            new_week += new_string
        self.week = new_week

    def record(self):
        self.rearrange()
        rowdict = {"序号": self.no, "课程名称": self.name, "课程属性": self.property,
                   "课时": self.hour, "学分": self.credit, "开课周": self.week,
                   "星期节次": self.schedule, "教室": self.location, "主讲教师": self.teacher,
                   "课程大纲": "=HYPERLINK(\"http://jwxk.ucas.ac.cn/course/courseplan/" + \
                           self.no + "\", \"[课程大纲]\")",
                   "时间地点": "=HYPERLINK(\"http://jwxk.ucas.ac.cn/course/coursetime/" + \
                           self.no + "\", \"[时间地点]\")",
                   "联系方式": "=HYPERLINK(\"http://jwxk.ucas.ac.cn/course/courseteacher/" + \
                           self.no + "\", \"[联系方式]\")"}
        # print(rowdict)
        self.table.record_dict(rowdict)

    def pipeline(self):
        stop = False
        while not stop:
            if self._attempt == self._max_attempts:
                self._existence = True
                self.name = "网络故障，信息获取失败"
                self.record()
                return  # 达到最大尝试次数说明网络错误，直接记录空白内容
            stop = self.get_outline() and self.get_schedule()  # 两个都成功时，停止
        if self.check_existence():
            self.get_info()
            self.record()
            return  # 记录并返回
        else:
            return  # 如果课程不存在


class CSVTable():
    def __init__(self, filename, colnames):
        self.filename = filename
        self.colnames = colnames

    def create(self):
        try:
            with open(self.filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.colnames)
            print("已创建文件：" + self.filename)
        except IOError:
            print("未创建文件：" + self.filename)
        return

    def record_dict(self, rowdict):
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.colnames)
            writer.writerow(rowdict)

    def record_list(self, rowlist):
        rowdict = {}
        for i in range(len(self.colnames)):
            rowdict.update({self.colnames[i]:rowlist[i]})
        self.record_dict(rowdict)


def percentage(now, all, tip="Progress: ", info=" "):
    now = now + 1
    percent = 1.0 * int(now) / int(all)
    sys.stdout.write("\r{0}{1}{2}{3}".format(tip,
                                             "|" * int(percent // 0.05),
                                             '%.2f%%' % (percent * 100),
                                             " (" + info + ")"))
    sys.stdout.flush()


class Finder():
    def __init__(self, start=0, end=0, filename=""):
        self.start = start
        self.end = end
        self.filename = filename
        self._length = self.end - self.start
        self.now = start

    def input(self):
        help_info = """
==课程网站小助手 V2.2.1==
输入数值范围在国科大课程网站中搜索本科生/研究生课程
模式：默认手动输入，T测试，L读档，Q退出
开始和结束值均包含在搜索范围之中
建议使用 Microsoft Office Excel 的筛选功能处理表格
首次使用请先测试
如果没有完整运行请重新打开使用继续模式
举例：
从153303到158499是2018-2019春季学期本科课程
从163564到164506是2019-2020秋季学期本科课程
"""
        print(help_info)
        mode = input("[模式选择：默认手动，T测试，L读档，Q退出] ")
        if mode == "":
            pass
        elif mode.lower()[0] == 't':
            self.test()
            self.input()
            return
        elif mode.lower()[0] in ['c', 'l']:
            self.load()
            return
        elif mode.lower()[0] == 'q':
            input("[回车以退出]")
            return
        self.start = int(input("[开始值：] "))
        if self.start < 0:
            self.start = 0
        elif self.start == 250:
            print("韩大佬是我儿子")
        self.now = self.start
        self.end = int(input("[结束值：] "))
        self.filename = '课程信息_' + str(self.start) + '-' + str(self.end) + \
               "_" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.csv'
        self.end += 1  # 结束值进行了修正，更符合常理
        self._length = self.end - self.start
        self.run()
        input("[运行完毕，回车退出]")

    def run(self):
        colnames = ["序号", "课程名称", "课程属性", "课时",
                    "学分", "开课周", "星期节次", "教室",
                    "主讲教师", "课程大纲", "时间地点", "联系方式"]
        tb = CSVTable(self.filename, colnames)
        if self.now == self.start:
            tb.create()
        for now in range(self.now, self.end):
            self.now = now
            cs = Course(now, tb)
            cs.pipeline()
            if cs.isexist():
                info = cs.no + "|" + cs.name
            else:
                info = cs.no
            percentage(self.now-self.start, self._length, tip="进度：", info=info)
            self.autosave()

    def autosave(self):
        log = "==课程网站小助手存档文件=="
        log += "\n文件名：" + self.filename
        log += "\n开始值：" + str(self.start)
        log += "\n结束值：" + str(self.end)
        log += "\n当前进度：" + str(self.now)
        with open("运行存档.log", "w") as savefile:
            savefile.write(log)
			
    def load(self):
        try:
            with open("运行存档.log", "r") as savefile:
                log = savefile.read()
                print("[读取成功]\n" + log)
        except FileNotFoundError:
            input("[读取失败]存档不存在！")
            return
        loglist = log.splitlines()
        self.filename = loglist[1][4:]
        self.start = int(loglist[2][4:])
        self.end = int(loglist[3][4:])
        self.now = int(loglist[4][5:])
        self._length = self.end - self.start
        self.run()

    @staticmethod
    def test():
        print("正在进行第一个测试，请稍后……")
        Finder(163564, 163576, "测试结果.csv").run()
        input("[测试完毕，回车继续]")

    @staticmethod
    def test_B():
        print("\n正在进行第二个测试，请稍后……")
        colnames = ["序号", "课程名称", "课程属性", "课时",
                    "学分", "开课周", "星期节次", "教室",
                    "主讲教师", "课程大纲", "时间地点", "联系方式"]
        tb = CSVTable("测试结果B.csv", colnames)
        no_list = list(range(1000000, 1000010)) + list(range(163600, 163610)) + \
                  list(range(165400, 165410)) + list(range(158400, 158410))
        for no in no_list:
            Course(no, tb).pipeline()
        input("[测试完毕，回车继续]")


Finder().input()

"""
版本信息：
V1.0.0（20190706）输入开始和结束值，搜索课程编号、名称、学期、代码
V1.1.0（20190706）新增课程大纲和时间安排的网址
V1.2.0（20190706）将网址改为Excel超链接
V1.3.0（20190706）加入自动测试
V1.3.2（20190706）加入彩蛋
V1.4.0（20190706）加入课程教师信息的链接，出于信息的保护，这个链接需登录sep系统粘贴到地址栏打开
V1.5.0（20190708）增加了把网络故障部分重新搜索的功能
V2.0.0（20190815）用新的编程思路重写内容，并增加了大量搜索信息
V2.1.0（20190816）优化了输出表格，做了一些其他调整
V2.2.0（20190816）缩减输出文件中繁琐的内容，增加进度存取功能
V2.2.1（20190816）修复问题

未来更新：
V2.3.0（20190817）加入打印可视化课程表的功能
"""
