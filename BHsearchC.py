from BHsearchBeta import *
import re

class CandidateCharlie(Candidate):  # 黑洞候选体，对应一个成语，getinfo用到具体网站
    def __str__(self):
        return Candidate.__str__(self) + " " + str(self.pinyin)

    def getinfo(self):  # 获取黑洞信息
        try:
            soup = BeautifulSoup(urlopen(self.link), "html.parser")
            raw_pinyin_lst = re.findall("【拼音】.*<", str(soup))
            if raw_pinyin_lst != []:
                self._raw_pinyin = raw_pinyin_lst[0][5:-1]
                if self._raw_pinyin != "":
                    self.regulate()
                    return
            print("\n[Empty Spectrum] " + str(self.word))
            logger("[Empty Spectrum]", str(self.word))
        except HTTPError as e:
            print("\n[HTTPError] " + str(self))
            logger("[HTTPError]", str(self))
        """
        以上需要用bs4从链接中获取成语信息
        """

    def __str__(self):
        return Candidate.__str__(self) + " " + str(self.pinyin)


class ObserverCharlie(Observer):  # 观测者，寻找黑洞候选体，并且放入星表中，用到具体网站
    def __init__(self):
        self.reglst = self.mkreglst()
        Observer.__init__(self, 8, 300)

    def mkreglst(self):
        soup = BeautifulSoup(urlopen("http://www.guoxuedashi.com/chengyu/"), "html.parser")
        reglst = []
        for tag in soup.findAll("", {"target": "_blank"}):
            tag = str(tag)
            i = 0  # i表示在字符串中的位置
            j = 0  # j表示第j个引号
            for char in tag:
                if char == '"':
                    j += 1  # 表示这是第j+1个引号
                    if j == 1:
                        start = i+1
                    elif j == 2:
                        end = i
                i += 1  # 将字符串中的位置定出
            reglst.append(tag[start:end])
        return reglst[:421]

    def _name(self):
        self.region = "http://www.guoxuedashi.com" + self.reglst[self._no]

    def _observe(self):  # 观测这一区域
        print("\n\n[Tip] Start observation on region " + str(self._no))
        logger("[Tip]", "Start observation on region " + str(self._no))
        if self.region == "":  # 如果这一区域不存在
            print("[RegionError] Region " + str(self._no) + " not exist")
            logger("[RegionError]", "Region " + str(self._no) + " not exist")
            return
        soup = BeautifulSoup(urlopen(self.region), "html.parser")
        length = len(soup.findAll('', {'target': '_blank'})[8:-21])
        now = 0
        for tag in soup.findAll('', {'target': '_blank'})[8:-21]:
            word = tag.string
            tag = str(tag)
            i = 0  # i表示在字符串中的位置
            j = 0  # j表示第j个引号
            for char in tag:
                if char == '"':
                    j += 1  # 表示这是第j+1个引号
                    if j == 1:
                        start = i+1
                    elif j == 2:
                        end = i
                i += 1  # 将字符串中的位置定出
            link = "http://www.guoxuedashi.com" + tag[start:end]
            candidate = CandidateCharlie(link=link, word=word)
            candidate.getinfo()
            percentage(now, length, tip=str(self._no)+":", info=str(candidate))
            now += 1
            yield candidate

    @staticmethod
    def plan():
        print("Black Hole Observatory Charlie (20190810)")
        print("Based on http://www.guoxuedashi.com")
        ObserverCharlie().pipeline()


if __name__ == '__main__':
    ObserverCharlie.plan()
