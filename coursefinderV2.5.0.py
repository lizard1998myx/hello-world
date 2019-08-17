from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import csv, datetime, sys


def main():
    Finder().interface()


class Course():
    """
    课程类，用于存放课程信息，并将课程信息录入到表格文件中
    """
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
        self.table = table  # csvTable对象，用于存储信息

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
            else:
                info = info + "|" + str
        return info

    def get_info(self):
        self.name = self._outline_soup.find('', {'class': 'mc-body'}).h4.get_text()
        self.code = self._outline_info("课程编码：")
        self.hour = self._outline_info("课时：")
        self.credit = self._outline_info("学分：")
        self.property = self._outline_info("课程属性：")
        self.teacher = self._outline_info("主讲教师：")
        self.term = self._schedule_soup.find('', {'class': 'mc-body'}).find_all_next()[1].get_text().replace("：", "")
        self.week = self._schedule_info("上课周次")
        self.schedule = self._schedule_info("上课时间")
        self.location = self._schedule_info("上课地点")

    def rearrange(self):  # 优化输出结果，例如开课周信息
        self.name = self.name.replace('•','·')  # 解决一个输出结果的bug
        if self.week != "":
            new_week = ""
            new_week_list = []
            for week in self.week.split("|"):
                new_string = ""
                start = -1
                last = -1
                for n in week.split("、") + [-1]:
                    n = int(n)
                    if start == -1:
                        start = n
                    elif n != last + 1:  # 如果不连续，返回之前连续部分，结尾为-1，一定不连续
                        if new_string != "":
                            new_string += ", "
                        if start == last:
                            new_string += str(start)
                        else:
                            new_string += str(start) + "-" + str(last)
                        start = n
                    last = n
                new_week_list.append(new_string)
            for new_string in new_week_list:
                if new_week != "":
                    new_week += "|"
                new_week += new_string
            self.week = "'" + new_week

    def record(self):
        self.rearrange()
        rowdict = {"序号": self.no, "课程名称": self.name, "课程属性": self.property, "选中": "1",
                   "课时": self.hour, "学分": self.credit, "开课周": self.week, "开课学期": self.term,
                   "星期节次": self.schedule, "教室": self.location, "主讲教师": self.teacher, "课程代码": self.code,
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
                self.term = "网络/网页故障，信息获取失败"
                if not self.get_outline():
                    self._existence = True
                    self.record()
                elif self.check_existence():
                    self.record()
                return  # 达到最大尝试次数说明网络错误，直接记录空白内容
            stop = self.get_outline() and self.get_schedule()  # 两个都成功时，停止
            self._attempt += 1
        if self.check_existence():
            self.get_info()
            self.record()
            return  # 记录并返回
        else:
            return  # 如果课程不存在


class CSVTable():
    """
    CSV表格类，用于创建和保存信息到表格
    由于读取需求不大，没有加入读取信息的模块
    """
    def __init__(self, filename, colnames):
        self.filename = filename
        self.colnames = colnames

    def create(self):
        try:
            with open(self.filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.colnames)
            print("已创建文件：" + self.filename)
        except PermissionError:
            print("[拒绝访问] 创建(" + self.filename + ")失败")
            input("请排除故障后回车以继续 ")
            self.create()
            return
        except IOError:
            print("[创建失败] 未创建文件：" + self.filename)
        return

    def record_dict(self, rowdict):
        try:
            with open(self.filename, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.colnames)
                writer.writerow(rowdict)
        except PermissionError:
            print("[拒绝访问] 将信息录入到(" + self.filename + ")失败")
            input("请排除故障后回车以继续 ")
            self.record_dict(rowdict)

    def record_list(self, rowlist):
        rowdict = {}
        for i in range(len(self.colnames)):
            rowdict.update({self.colnames[i]: rowlist[i]})
        self.record_dict(rowdict)


def percentage(now, all, tip="Progress: ", info=" "):
    """
    常用的工具函数，用于显示进度条，需要用到sys.stdout库
    :param now: 目前的进度，从0开始
    :param all: 列表的总长度
    :param tip: 在进度条前端显示的标识
    :param info: 在进度条后端显示的信息，用括号围住
    :return:
    """
    now = now + 1
    percent = 1.0 * int(now) / int(all)
    sys.stdout.write("\r{0}{1}{2}{3}".format(tip,
                                             "|" * int(percent // 0.05),
                                             '%.2f%%' % (percent * 100),
                                             " (" + info + ")"))
    sys.stdout.flush()


class Finder():
    """
    课程搜索器类
    这是交互的核心
    基本的搜索功能是创建表格类并调用课程类来实现搜索信息的功能
    实现存档功能，出现问题可以读档继续
    通过调用打印机类来预览课程表
    """
    def __init__(self, start=0, end=0, filename=""):
        self.start = start
        self.end = end
        self.filename = filename
        self._length = self.end - self.start
        self.now = start

    def interface(self):
        print(instruction())
        mode = input("[模式选择：] ")
        if mode == "":
            pass
        elif mode.lower()[0] == 't':
            self.test()
            self.interface()
            return
        elif mode.lower()[0] in ['c', 'l']:
            self.load()
            input("[回车以运行]")
            self.run()
            return
        elif mode.lower()[0] == 'p':
            input_file = input("[载入表格文件名：] ")
            if input_file != "":
                Printer(input_file).run()
            else:
                self.load()
                Printer(self.filename).run()
            input("[回车以退出]")
            return
        elif mode.lower()[0] == 'h':
            print(help_info())
            input("[回车以返回]")
            self.interface()
            return
        elif mode.lower()[0] == 'v':
            print(version_info())
            input("[回车以返回]")
            self.interface()
            return
        elif mode.lower()[0] == 'q':
            input("[回车以退出]")
            return
        self.start = int(input("[开始值：] "))
        if self.start < 0:
            self.start = 0
        elif self.start == 250:
            print("[这真的不是彩蛋，但是韩大佬是我儿子]")
        self.now = self.start
        self.end = int(input("[结束值：] "))
        self.filename = '课程信息_' + str(self.start) + '-' + str(self.end) + \
                        "_" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.csv'
        self.end += 1  # 结束值进行了修正，更符合常理
        self._length = self.end - self.start
        self.run()
        input("\n[运行完毕，回车退出]")

    def run(self):
        colnames = ["序号", "开课学期", "课程代码", "课程名称", "课程属性", "课时",
                    "学分", "开课周", "星期节次", "教室",
                    "主讲教师", "课程大纲", "时间地点", "联系方式", "选中"]
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
            percentage(self.now - self.start, self._length, tip="进度：", info=info)
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
            input("[读取失败] 存档不存在！")
            return
        loglist = log.splitlines()
        self.filename = loglist[1][4:]
        self.start = int(loglist[2][4:])
        self.end = int(loglist[3][4:])
        self.now = int(loglist[4][5:])
        self._length = self.end - self.start

    @staticmethod
    def test():
        print("[测试开始] 正在进行测试，请稍后……")
        Finder(163564, 163576, "测试结果.csv").run()
        print()
        Printer("测试结果.csv").run()
        input("[测试完毕，回车继续]")


class CourseSimplified(Course):
    """
    简化的课程类，只保存需要打印的信息，节省空间
    将标准的上课时间转化为坐标放入课程表中，若上课时间不标准会出错
    可以生成带有坐标的课程类，对应不同的开课周
    默认建立空课程类
    """
    def __init__(self, no="", name="", teacher="", schedule="", week="", row=0, col=0):
        self.no = no
        self.name = name
        self.schedule = schedule
        self.teacher = teacher
        self.chosen = True
        self.line_length = 3
        self.week = week
        self.col = col
        self.row = row

    def get_coordinate(self):
        if self.schedule == "":
            return []
        coordinate_list = []
        rawlist = self.schedule.replace('日', '0').replace('一', '1').replace('二', '2')\
            .replace('三', '3').replace('四', '4').replace('五', '5').replace('六', '6').split('|')
        for rawschedule in rawlist:
            col = int(rawschedule[2])
            for row in rawschedule[6:-2].split('、'):
                coordinate_list.append((col, int(row)))
        return coordinate_list

    def coordinated_courses_iter(self):
        if self.isempty() or self.schedule == "":
            return
        schedule_list = self.schedule.replace('日', '0').replace('一', '1').replace('二', '2')\
            .replace('三', '3').replace('四', '4').replace('五', '5').replace('六', '6').split('|')
        week_list = self.week.split('|')
        if week_list == []:
            for i in range(len(schedule_list)):
                week_list.append("")
        elif len(week_list) < len(schedule_list):
            for i in range(len(schedule_list)-len(week_list)):
                week_list.insert(0, week_list[0])
        for i in range(len(schedule_list)):
            col = int(schedule_list[i][2])  # 星期X
            for row in schedule_list[i][6:-2].split('、'):
                row = int(row)  # 第Y节
                yield CourseSimplified(no=self.no, name=self.name, teacher=self.teacher,
                                       week=week_list[i], row=row, col=col)

    def isempty(self):
        return self.no==''

    def get_lines(self):
        lines = []
        if self.isempty():
            for i in range(self.line_length):
                lines.append("")
        else:
            lines.append("=HYPERLINK(\"http://jwxk.ucas.ac.cn/course/courseplan/" + self.no + "\", \"[" + self.no + "]\")")
            lines.append(self.name+"["+self.teacher+"]")
            lines.append("'" + self.week)
        return lines


class CourseQueue(list):
    """
    课程队列类，课程表的每一个格子有一个课程队列类
    从源表格读取信息时入队，打印时使用出队，若为空对，会返回一个空课程对象
    """
    def isempty(self):
        return len(self)==0

    def enqueue(self, element):
        self.append(element)

    def dequeue(self):
        if self.isempty():
            return CourseSimplified()  # return an empty class
        else:
            return self.pop(0)


class CourseTable(list):
    """
    课程表类，列表的子类，基本格式为二维列表
    列是星期X，行是第Y节课，self[X][Y]为星期X第Y节课
    第0-6列表示星期日到星期六
    第0行设计为空，1-12行对应第1-12节课
    使用csv库的字典模式读取源表格被选课程的信息
    """
    def __init__(self):
        list.__init__(self)
        self.col = 7
        self.row = 12+1
        for col in range(self.col):
            column = []
            for row in range(self.row):
                column.append(CourseQueue())
            self.append(column)

    def isemptyrow(self, row):
        for col in range(self.col):
            if not self[col][row].isempty():
                return False
        return True

    def poprow(self, row):
        row_list = []
        for col in range(self.col):
            row_list.append(self[col][row].dequeue())
        return row_list

    def load(self, element, col, row):
        self[col][row].enqueue(element)

    def read(self, filename):
        print('正在读取，请稍后……')
        with open(filename, 'r') as csvfile:
            for course_info in csv.DictReader(csvfile):
                course = CourseSimplified(no=course_info['序号'], name=course_info['课程名称'],
                                          teacher=course_info['主讲教师'], schedule=course_info['星期节次'],
                                          week=course_info['开课周'].replace("'",""))
                try:
                    key = course_info['选中']
                    if key == "" or key == "0":
                        course.chosen = False  # 如果‘选中’列空或为0，则选中本课
                except KeyError:
                    pass  # 如果‘选中’列不存在，则默认选中本课
                if course.chosen:
                    for coor_course in course.coordinated_courses_iter():
                        self.load(coor_course, col=coor_course.col, row=coor_course.row)


class Printer():
    """
    打印机类
    设置输入文件名和输出文件名，建立输出CSV表格对象
    访问课程表得到简化课程对象，访问这些对象来获取信息，从而逐行打印
    """
    def __init__(self, input, output=''):
        if 'csv' not in input:
            input += '.csv'
        self.input = input
        if output == "":
            if "课程信息" in input:
                output = input.replace('课程信息', '课程表')
            else:
                output = input.replace('.csv', '_课程表.csv')
        elif 'csv' not in output:
            output += '.csv'
        self.output = CSVTable(output, ['节次', '星期日', '星期一', '星期二',
                                        '星期三', '星期四', '星期五', '星期六'])
        self.output.create()
        self.coursetable = CourseTable()
        self.row = 0
        self._max_row_index = 12

    def printline(self):
        """
        从课程表中获取信息，并且打印一行
        打印信息在Course对象中分类
        :return:
        """
        if self.row == 0 or self.coursetable.isemptyrow(self.row):
            self.nextline()
        else:
            course_list = self.coursetable.poprow(self.row)

            for line in range(course_list[0].line_length):
                list_to_print = [str(self.row)]
                for course in course_list:
                    list_to_print.append(course.get_lines()[line])
                self.output.record_list(list_to_print)


    def nextline(self):
        """
        跳到下一行，并打印一行以新行标为首的空行
        :return:
        """
        self.row += 1
        if self.row <= self._max_row_index:
            self.output.record_list([str(self.row), '', '', '', '', '', '', ''])

    def run(self):
        self.coursetable.read(self.input)
        while self.row <= self._max_row_index:
            self.printline()


def instruction():
    """
    打开软件时给的直观指示
    :return:
    """
    return """
==课程网站小助手 V2.5.0==
输入数值范围，在国科大课程网站中搜索本科生/研究生课程

[使用实例]
1）先运行测试（T）并理解所生成的文件
2）在默认模式输入 163564 到 164505 搜索2019秋季学期本科课程
3）如果运行闪退，重开软件并读档（L）
4）运行结束后，用 Excel 的筛选功能选出感兴趣的课
5）将感兴趣的课末尾的“选中”列设为1，其他的课删掉或者将“选中”值清空
6）保存到原文件，然后重开软件进入打印模式（P）一路回车，生成课程表预览

[注意事项]
1）其他搜索范围可以获得各学期本科生/研究生课程
2）联系方式的超链接无法直接打开，需登录sep后粘贴地址手动打开
3）Microsoft Office Excel 能直接进入超链接，WPS可能不行
4）搜索过程中打开生成表格会闪退，可以通过重开读档解决
5）修改表格文件的内容或格式都有可能导致打印功能无法正常使用
6）保存为csv可能导致超链接异常，打印前请备份原文件

[模式选择]
默认模式手动输入始末值
测试（T），读档（L），打印（P），退出（Q）
显示完整帮助（H），显示版本信息（V）
"""


def help_info():
    """
    完整的帮助和参考信息
    :return:
    """
    return """
[完整帮助信息]
默认模式根据所输入的开始和结束值进行搜索，首尾都在搜索范围中
测试模式（T）运行指定范围的搜索，生成表格和课程表预览
读档（L）根据当前目录的“运行存档.log”文件继续搜索，不会破坏已搜到的信息
读档功能的高级用法是手动修改存档，使搜索从指定位置开始
打印模式（P）是从指定的csv表格文件中生成课程表供预览
如果没有指定文件，打印模式会从存档中直接读取文件名并生成课程表

[搜索范围参考]
从49669到53393是2004-2005学年远古研究生课程
从75830到77764是2010-2011秋季学期研究生课程
从153303到158499是2018-2019春季学期本科课程
从163564到164505是2019-2020秋季学期本科课程

[反馈]
这个工具是作者学习Python过程中做的练习，原理并不复杂
使用小工具过程中，若遇到任何问题或有想分享的东西
欢迎联系我 o(*￣▽￣*)ブ
mengyuxi16@mails.ucas.ac.cn
"""


def version_info():
    """
    显示版本更新信息
    :return:
    """
    return """
[部分版本信息]
V1.0.0（20190706）搜索课程编号、名称、学期、代码
V1.1.0（20190706）新增课程大纲和时间安排的网址
V1.2.0（20190706）将网址改为Excel超链接
V1.3.0（20190706）加入测试模式
V1.3.2（20190706）加入彩蛋
V1.4.0（20190706）加入课程教师信息的链接，出于信息的保护，它需登录sep系统后粘贴到地址栏打开
V1.5.0（20190708）增加了把网络故障部分重新搜索的功能
V2.0.0（20190815）用面向对象的编程思路重写内容，并增加了大量搜索信息
V2.1.0（20190816）优化了输出表格，做了一些其他调整
V2.2.0（20190816）缩减输出的冗余内容，加入存档读档功能
V2.2.2（20190816）修复输出时部分字符无法解码等问题
V2.3.0（20190816）加入课程表打印机
V2.3.1（20190816）修复输出周数的问题，恢复开课学期的显示
V2.4.0（20190816）优化选课方式和帮助信息
V2.4.4（20190817）修复大量问题，优化输出，补充源码注释
V2.5.0（20190819）修改开课周输出，加强课程表预览

[未来更新计划]
V2.6.0+（？）弃用csv，直接保存为xls等格式，更易于操作
"""


if __name__ == '__main__':
    main()
