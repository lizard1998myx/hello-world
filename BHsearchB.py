from urllib.error import URLError
from BHsearchA import *


class CandidateBeta(Candidate):  # 黑洞候选体，对应一个成语，getinfo用到具体网站
    def getinfo(self):  # 获取黑洞信息
        soup = BeautifulSoup(self.link, "html.parser",from_encoding='gb18030')
        word_tag = soup.find("", {"color":"red"})  # 默认读取方式，如"http://cy.5156edu.com/html4/2.html"
        raw_pinyin_tag = soup.find("", {"width": "40%"})
        if word_tag is None or word_tag.contents[0]=="手机版":  # 第二种类型的网页，如"http://cy.5156edu.com/html4/983.html"
            word_tag = soup.find("", {"class": "font_22"})
            raw_pinyin_tag = soup.find("", {"class": "font_18"})
        if word_tag is not None:
            self.word = word_tag.contents[0].contents[0]
            if raw_pinyin_tag is not None:
                self._raw_pinyin = raw_pinyin_tag.contents[0]
                self.regulate()
            else:
                print("\n[Empty Spectrum] " + self.word)
                logger("[Empty Spectrum]", self.word)
        else:  # 其他类型的网页
            print("\n[Empty Name] " + self.link.url)
            logger("[Empty Name]", self.link.url)
        """
        以上需要用bs4从链接中获取成语信息
        """

    def __str__(self):
        return Candidate.__str__(self) + " " + str(self.pinyin)


class ObserverBeta(Observer):  # 观测者，寻找黑洞候选体，并且放入星表中，用到具体网站
    def __init__(self):
        Observer.__init__(self, 1, 31250)
        self.region = "Disabled"
        self.target = ""  # 天体坐标链接

    def state(self):
        return [str(self._no),self.target]

    def _name(self):
        self.target = "http://cy.5156edu.com/html4/" + str(self._no) + ".html"

    def _observe(self):  # 观测这一区域
        try:
            html = urlopen(self.target)
            candidate = CandidateBeta(link=html)
            candidate.getinfo()
            percentage(self._no, self._length, info=str(self._no) + "|" + str(candidate))
            yield candidate
        except HTTPError:
            pass
        except URLError:
            pass  # URLError 通常只是这个网址不存在而已，因此直接跳过
        except BaseException as e:  # 记录其他故障
            print("[Unknown Error]")
            logger("[Unknown Error]" + str(self.state()), str(e))
        """
        以上是在这一区域中，使用bs4获得每个成语的链接，并且制成黑洞候选体
        然后利用candidate的操作获取黑洞候选体的信息
        再将候选体反馈给观测者
        """

    @staticmethod
    def plan():
        print("Black Hole Observatory Beta (20190810)")
        print("Based on http://cy.5156edu.com")
        ObserverBeta().pipeline()


if __name__ == '__main__':
    ObserverBeta.plan()
