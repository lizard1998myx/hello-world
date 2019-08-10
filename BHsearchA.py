import sys
import csv
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError


def percentage(now, all, tip="Progress: ", info=" "):
    now = now + 1
    percent = 1.0 * int(now) / int(all)
    sys.stdout.write("\r{0}{1}{2}{3}".format(tip,
                                             "|" * int(percent // 0.05),
                                             '%.2f%%' % (percent * 100),
                                             " (" + info + ")"))
    sys.stdout.flush()


def logger_init():
    record_init('log.csv')


def logger(tag, info):
    record('log.csv', tag, info)


def record_init(filename):
    try:
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['TAG', 'INFO'])
    except IOError:
        pass  # 文件无法读取时，不进行初始化


def record(filename, tag, info):
    with open(filename, 'a') as csvfile:
        filenames = ['TAG', 'INFO']
        writer = csv.DictWriter(csvfile, fieldnames=filenames)
        writer.writerow({'TAG': tag, 'INFO': info})


class Candidate():  # 黑洞候选体，对应一个成语，getinfo用到具体网站
    def __init__(self, link="", word=""):
        self.link = link  # 天体坐标
        self.word = word  # 天体光度
        self.pinyin = []  # 天体光谱
        self._raw_pinyin = ""

    def __str__(self):
        return self.word + " " + self._raw_pinyin

    def getinfo(self):  # 获取黑洞信息
        try:
            soup = BeautifulSoup(urlopen(self.link), "html.parser")
            raw_pinyin_tag = soup.find('pinyin')
            if raw_pinyin_tag is not None:
                self._raw_pinyin = soup.find('pinyin').contents[0]
                self.regulate()
            else:
                print("\n[Empty Spectrum] " + self.word)
                logger("[Empty Spectrum]", self.word)
        except HTTPError as e:
            print("\n[HTTPError] " + self.word)
            logger("[HTTPError]", self.word)
        """
        以上需要用bs4从链接中获取成语信息
        """

    def regulate(self):
        # 把拼音的注音去掉
        raw_pinyin = self._raw_pinyin
        raw_pinyin = raw_pinyin.replace('ā', 'a')
        raw_pinyin = raw_pinyin.replace('á', 'a')
        raw_pinyin = raw_pinyin.replace('ǎ', 'a')
        raw_pinyin = raw_pinyin.replace('à', 'a')
        raw_pinyin = raw_pinyin.replace('ō', 'o')
        raw_pinyin = raw_pinyin.replace('ò', 'o')
        raw_pinyin = raw_pinyin.replace('ǒ', 'o')
        raw_pinyin = raw_pinyin.replace('ó', 'o')
        raw_pinyin = raw_pinyin.replace('ē', 'e')
        raw_pinyin = raw_pinyin.replace('é', 'e')
        raw_pinyin = raw_pinyin.replace('ě', 'e')
        raw_pinyin = raw_pinyin.replace('è', 'e')
        raw_pinyin = raw_pinyin.replace('ī', 'i')
        raw_pinyin = raw_pinyin.replace('í', 'i')
        raw_pinyin = raw_pinyin.replace('ǐ', 'i')
        raw_pinyin = raw_pinyin.replace('ì', 'i')
        raw_pinyin = raw_pinyin.replace('ū', 'u')
        raw_pinyin = raw_pinyin.replace('ú', 'u')
        raw_pinyin = raw_pinyin.replace('ǔ', 'u')
        raw_pinyin = raw_pinyin.replace('ù', 'u')
        raw_pinyin = raw_pinyin.replace('ǖ', 'v')
        raw_pinyin = raw_pinyin.replace('ǘ', 'v')
        raw_pinyin = raw_pinyin.replace('ǚ', 'v')
        raw_pinyin = raw_pinyin.replace('ǜ', 'v')
        raw_pinyin = raw_pinyin.replace('ü', 'v')

        self.pinyin = []
        str = ""
        for char in raw_pinyin:
            if char.isspace() or char in [',', '，']:  # 如果是空格或逗号
                if str != "":
                    self.pinyin.append(str)
                    str = ""
            else:  # 如果是拼音字符
                str = str + char
        if str != "":
            self.pinyin.append(str)

        """
        # Original
        self.pinyin = []
        str = ""
        for char in raw_pinyin:
            if char != " ":
                str = str + char
            if char == " ":
                self.pinyin.append(str)
                str = ""
        self.pinyin.append(str)
        """

    def getfirst(self):
        return self.pinyin[0]

    def getlast(self):
        return self.pinyin[-1]

    def isempty(self):
        return self._raw_pinyin == ""


class SpecType():  # 光谱型，对应一种光谱（拼音），有可能是黑洞，也可能不是
    def __init__(self, pinyin=""):
        self.pinyin = pinyin  # 黑洞类型，即拼音
        self._first = 0  # 在开头出现的次数
        self._last = 0  # 在结尾出现的次数

    def addfirst(self, n=1):
        self._first += int(n)

    def addlast(self, n=1):
        self._last += int(n)

    def isbh(self):  # 黑洞定义：没有以这一发音开头，但有以这一发音结尾的一类天体
        return self._first==0 and self._last>0

    def total(self):
        return self._first + self._last

    def report(self):
        print("Spectral Type: " + self.pinyin)
        print("as first = " + str(self._first))
        print("as last  = " + str(self._last))


class Catalogue(list):  # 星表，记录各类光谱型出现数量
    def _load_first(self, first_pinyin):  # 当拼音在首字出现
        for spt in self:
            if first_pinyin == spt.pinyin:
                spt.addfirst()
                return
        new_spt = SpecType(first_pinyin)
        new_spt.addfirst()
        self.append(new_spt)

    def _load_last(self, last_pinyin):  # 当拼音在末尾出现
        for spt in self:
            if last_pinyin == spt.pinyin:
                spt.addlast()
                return
        new_spt = SpecType(last_pinyin)
        new_spt.addlast()
        self.append(new_spt)

    def load(self, candidate):  # 将候选体的信息录入到星表
        if candidate.pinyin != []:
            self._load_first(candidate.getfirst())
            self._load_last(candidate.getlast())

    def makemap(self):  # 将星表中出现的真实黑洞列成表
        map = []
        for spt in self:
            if spt.isbh():
                map.append(spt.pinyin)
        return map


class Observer():  # 观测者，寻找黑洞候选体，并且放入星表中，用到具体网站
    def __init__(self, min=27, max=422):
        self._min = min
        self._max = max
        self._length = self._max - self._min + 1
        self.catalog = Catalogue()
        self.region = ""  # 天区，在天区中有若干个黑洞候选体
        self._no = self._min  # 天区坐标，使用时，26为空白天区，27开始是实际天区
        self._map = []  # 黑洞地图，用于寻找黑洞
        self._name()
        
    def state(self):
        return [str(self._no),self.region]

    def setno(self, no=-1):
        if no < 0:
            no = self._min
        self._no = no
        self._name()

    def _name(self):
        self.region = "https://m.chazidian.com/chengyu_a_" + str(self._no) + "/"

    def next(self):  # 进入下个区域/对准下个目标
        self._no += 1
        if self._no <= self._max:
            self._name()
            return True
        else:
            return False

    def _observe(self):  # 观测这一区域
        print("\n\n[Tip] Start observation on region " + str(self._no))
        logger("[Tip]", "Start observation on region " + str(self._no))
        if self.region == "":  # 如果这一区域不存在
            print("[RegionError] Region " + str(self._no) + " not exist")
            logger("[RegionError]", "Region " + str(self._no) + " not exist")
            return
        soup = BeautifulSoup(urlopen(self.region), "html.parser")
        taglist = soup.findAll('', {'class': 'list_016'})
        length = len(taglist)
        now = 0
        for tag in taglist:
            word = tag.string
            tag = str(tag)
            i = 0  # i表示在字符串中的位置
            j = 0  # j表示第j个引号
            for char in tag:
                if char == '"':
                    j += 1  # 表示这是第j+1个引号
                    if j == 3:
                        start = i+1
                    elif j == 4:
                        end = i-1
                i += 1  # 将字符串中的位置定出
            link = tag[start:end].replace('m.','www.')
            candidate = Candidate(link=link, word=word)
            candidate.getinfo()
            percentage(now, length, tip=str(self._no)+":", info=str(candidate))
            now += 1
            yield candidate
        """
        以上是在这一区域中，使用bs4获得每个成语的链接，并且制成黑洞候选体
        然后利用candidate的操作获取黑洞候选体的信息
        再将候选体反馈给观测者
        """

    def work(self):  # 工作：观测并记录
        in_field_of_view = True
        while in_field_of_view:
            for candidate in self._observe():
                self.catalog.load(candidate)
            in_field_of_view = self.next()

    def report(self):
        self._map = self.catalog.makemap()
        total = str(self.total())
        print("\n[Total]" + total)
        logger("[Total]", total)
        print("[Black Hole Map]\n" + self._map)
        logger("[Black Hole Map]", self._map)

    def search(self):
        in_field_of_view = True
        while in_field_of_view:
            for candidate in self._observe():
                if not candidate.isempty():
                    if candidate.getlast() in self._map:  # 如果此候选体是黑洞
                        print("\n[Black hole] " + str(candidate))
                        logger("[Black Hole]", str(candidate))
            in_field_of_view = self.next()

    def manual_check(self, pinyin):
        for spt in self.catalog:
            if spt.pinyin == pinyin:
                spt.report()
                return
        print("Not found: " + pinyin)

    def total(self):
        n = 0
        for spt in self.catalog:
            n += spt.total()
        return n/2
    
    def working(self):
        try:
            self.work()
        except BaseException as e:
            print("[Work Error] " + str(self.state()) + str(e))
            logger("[Work Error]",str(e))
            logger(str(self.state()[0]),str(self.state()[1]))
            self.work()
    
    def searching(self):
        try:
            self.search()
        except BaseException as e:
            print("[Search Error] " + str(self.state()) + str(e))
            logger("[Search Error]"+str(self.state()),str(e))
            self.search()
            
    def pipeline(self):
        try:
            logger_init()
            self.working()  # 重复工作
            try:
                self.report()
            except BaseException as e:
                print("[Report Error] " + str(e))
                logger("[Report Error]", str(e))
            self.setno()
            self.searching()  # 重复搜寻
            while True:
                self.manual_check(input("Enter pinyin:"))
        except BaseException as e:
            print("[Pipeline Error] " + str(e))
            logger("[Pipeline Error]", str(e))
            logger(str(self.state()[0]), str(self.state()[1]))
        input("[Pipeline Done]\n")

    @staticmethod
    def plan():
        print("Black Hole Observatory Alpha (20190809)")
        print("Based on http://www.chazidian.com")
        Observer().pipeline()


if __name__ == '__main__':
    Observer.plan()
