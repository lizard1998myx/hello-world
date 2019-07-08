#!/data/data/com.termux/files/usr/bin/python3
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import csv, datetime, sys

def main():
    info()
    searcherio()

def searcherio():
    start = int(input("输入开始值："))
    if start == -1:
        tester()
    elif start == -2:
        redoer(input("请输入文件名："),mode=1)
    elif start == 250:
        print("韩大佬是我儿子")
    else:
        redoer(searcher(start, int(input("输入结束值："))+1),mode=0)
    input("\n任意键以退出")

def tester():
    """
    测试函数，生成测试表格，也可用于预览运行结果

    :return:
    """
    print("测试开始，请等待测试结果……")
    filename = 'Test_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.csv'
    listsearcher(filename,list(range(163600, 163610)) + list(range(165400, 165410)) + list(range(158400, 158410)))
    print('\n' + filename + " 已保存！测试完毕")
    return filename

def searcher(start, end):
    """
    利用listsearcher函数，搜索从start到end的课程
    保存到指定文件中

    :param start:
    :param end:
    :return:
    """
    filename = 'CourseInfo_' + str(start) + '-' + str(end) + \
               "_" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.csv'
    listsearcher(filename, range(start,end))
    return filename

def redoer(inputname, mode=0):
    """
    补充搜索器
    模式0表示自动进行，调用特殊combiner
    模式1表示手动进行，调用一般combiner

    :param inputname:
    :param mode:
    :return:
    """
    print("\n开始补充搜索……")
    outputname = inputname.replace(".csv","_add.csv")
    filename = inputname.replace(".csv","_comp.csv")
    listsearcher(outputname,errorreader(inputname))
    print()
    if mode == 0:
        csvcombiner_sp(inputname, outputname, filename)
    elif mode == 1:
        csvcombiner([inputname,outputname],filename)
    return filename

def listsearcher(filename, codelist):
    recorder_init(filename)

    #供进度条使用
    i = 0
    length = len(codelist)

    for Course_code in codelist:

        # 进度条显示器
        percent = 1.0 * (i + 1) / (length)
        sys.stdout.write("\r进度 {0}{1}{2}".format("|" * int(percent // 0.05),
                                                   '%.2f%%' % (percent * 100),
                                                   " (" + str(Course_code) + ")"))
        sys.stdout.flush()
        i = i+1

        recorder(filename, infofinder(Course_code))

def infofinder(Course_code):
    """
    核心代码，利用BeautifulSoup4
    搜索单个课程编码对应的课程名、学期信息、课程代码

    :param Course_code 课程编码:
    :return [找到与否, 课程编码, 课程名, 学期信息, 课程代码]:
    """
    Course_url = "http://jwxk.ucas.ac.cn/course/courseplan/" + str(Course_code) #课程大纲网址
    Course_term_url = "http://jwxk.ucas.ac.cn/course/coursetime/" + str(Course_code) #课程时间网址

    Course_name = "" #课程名
    Course_term = ""  # 学期信息/错误信息
    Course_sign = "" #课程代码

    try:
        html = urlopen(Course_url)
    except URLError as e:
        return [True, Course_code, Course_name, 'URLError', str(e)]

    bs0bj = BeautifulSoup(html, "html.parser")
    Course_name = str(bs0bj.find('', {'class': 'mc-body'}).h4.get_text()) #获取课程名

    if Course_name == "": #如果没东西
        return [False, Course_code, Course_name, Course_term, Course_sign]
    else:
        try:
            html_term = urlopen(Course_term_url)
        except HTTPError as e: #如果网络错误
            return [True, Course_code, Course_name, 'HTTPError', str(e)]
        except URLError as e:
            return [True, Course_code, Course_name, 'URLError', str(e)]
        else:
            bs0bj_term = BeautifulSoup(html_term, "html.parser") #这是用来干啥的？忘了

        Course_sign = str(bs0bj.find('', {'class': 'mc-body'}).span.get_text()) #获取课程信息
        Course_sign = Course_sign.replace("课程编码：", "")
        if Course_term == "":
            i = 0
            for sibling in bs0bj_term.find('', {'class': 'mc-body'}).p.next_siblings:
                i = i + 1
                if i == 2:
                    Course_term = str(sibling)[3:-5]

        return [True, Course_code, Course_name, Course_term, Course_sign]

def recorder_init(filename):
    """
    表格文件初始化
    创建表格文件，如果创建不成功会有相关提示

    :param filename:
    :return:
    """
    try:
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Course_code', 'Course_name', 'Course_term', 'Course_sign', 'outline', 'schedule', 'contact'])
        print("已创建文件：" + filename)
    except IOError:
        print("未创建文件：" + filename)
    return

def recorder(filename, infolist):
    """
    信息录入函数

    :param filename:
    :param infolist 见infofinder的返回值:
    :return:
    """
    if infolist[0]: #如果有课程信息就录入
        with open(filename, 'a') as csvfile:
            filenames = ['Course_code', 'Course_name', 'Course_term', 'Course_sign', 'outline', 'schedule', 'contact']
            writer = csv.DictWriter(csvfile, fieldnames=filenames)
            writer.writerow({'Course_code' : infolist[1],
                             'Course_name' : infolist[2],
                             'Course_term' : infolist[3],
                             'Course_sign' : infolist[4],
                             'outline'     : "=HYPERLINK(\"http://jwxk.ucas.ac.cn/course/courseplan/" + \
                                             str(infolist[1]) + "\", \"[Outline]\")",
                             'schedule'    : "=HYPERLINK(\"http://jwxk.ucas.ac.cn/course/coursetime/" + \
                                             str(infolist[1]) + "\", \"[Schedule]\")",
                             'contact'     : "=HYPERLINK(\"http://jwxk.ucas.ac.cn/course/courseteacher/" + \
                                             str(infolist[1]) + "\", \"[Contact]\")"
                             })

            return
    else:
        return

def errorreader(filename):
    """
    读取表格，将URLError的编码重新读取，输出一个列表

    :param filename:
    :return:
    """
    codelist = []

    try:
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for data in reader:
                if len(data) >= 1: # 非空行
                    if data[2] == 'URLError': #如果是错误
                        codelist.append(data[0])
            print(filename + " 读取完毕 :)")
    except IOError:
        print(filename + " 读取失败 :(")

    return codelist

def csvcombiner(inputlist, output):
    recorder_init(output)
    print("开始合并，请稍后……")
    for inputfile in inputlist:
        try:
            with open(inputfile, 'r') as csvfile:
                reader = csv.reader(csvfile) #获得输入表数据
                for data in reader: #逐行读取载入数据
                    if len(data) >= 1: # 非空行
                        recorder(output, [True]+data)
            print("已载入（" + inputfile + "）")
        except IOError:
            print("读取失败（" + inputfile + "）")
    print("合并完成！")

def csvcombiner_sp(filename_original, filename_add, output):
    recorder_init(output)
    print("开始合并，请稍后……")
    errorlist = errorreader(filename_original)

    try:
        with open(filename_original, 'r') as csvfile: #筛选地放入原数据
            reader = csv.reader(csvfile) #获得输入表数据
            for data in reader: #逐行读取载入数据
                if len(data) >= 1: # 非空行
                    if data[0] not in errorlist: #如果没有被补充搜索
                        recorder(output, [True]+data)
        print("已载入（" + filename_original + "）")
    except IOError:
        print("读取失败（" + filename_original + "）")

    try:
        with open(filename_add, 'r') as csvfile: #直接放入补充数据
            reader = csv.reader(csvfile) #获得输入表数据
            for data in reader: #逐行读取载入数据
                if len(data) >= 1: # 非空行
                    recorder(output, [True]+data)
        print("已载入（" + filename_add + "）")
    except IOError:
        print("读取失败（" + filename_add + "）")

    print("合并完成！")

def info():
    print("""
==课程网站小助手 V1.51==

【使用说明】
输入开始值和结束值即可进行课程的搜索
原理是到课程大纲和时间安排的页面获取课程信息
可以用于搜索中国科学院大学本科生和研究生的课程
通常在选课单下发前的一段时间就可以找到信息
运行时，会在目录生成一个表格文件，包括课程的相关信息
运行过程中如果出现错误，错误信息也会被保存到表格中
建议使用 Microsoft Office Excel 的筛选功能处理表格
可以先用测试器预览结果

开始和结束值举例：
153303-158498 2018-2019春季学期本科课程
163564-164505 2019-2020秋季学期本科课程

【版本信息】
V1.00 - 20190706
    输入开始和结束值，搜索课程编号、名称、学期、代码
V1.10 - 20190706
    新增课程大纲和时间安排的链接
V1.11 - 20190706
    修复一个漏洞
V1.20 - 20190706
    优化超链接
V1.30 - 20190706
    添加测试器
    开始值为(-1)时，进行测试
V1.31 - 20190706
    为了防止结束值导致搜索不完全，实际值为输入值加一
    这次更新对强迫症非常不友好
V1.32 - 20190706
    加入了奇怪的东西
V1.40 - 20190706
    为方便同学和老师取得联系，加入了课程教师信息的链接
    可能出于个人信息的保护，这个链接无法直接打开
    亲测登录sep系统之后直接将链接粘贴到地址栏可以打开
V1.50 - 20170708
    增加了补充搜索的功能，将出现错误的项再搜索一次
    每次正常搜索过后会进行一次补充搜索
    输入(-2)调用独立的补充搜索功能
V1.51 - 20170708
    修复文件名输入错误时补充搜索无法进行的问题
    自动补充搜索在生成合并文件时不会重复加入

©2019 朝鲜世宗大王第一大学. All rights reserved.
    """)

main()
