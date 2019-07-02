import requests
import json
import time
import urllib
from langconv import Converter


class LagouSpider(object):
    def __init__(self, cityname, jobname):
        # 繁體轉簡體
        citynameconvertozn = Converter("zh-hans").convert(cityname)
        citynameconvertozn = citynameconvertozn.encode("utf-8")
        jobnameconvertozn = Converter("zh-hans").convert(jobname)
        jobnameconvertozn = jobnameconvertozn.encode("utf-8")

        # 再把簡體中文城市名及工作職位轉成url格式
        cityname_url = urllib.parse.quote(citynameconvertozn)
        jobname_url = urllib.parse.quote(jobnameconvertozn)

        self.cityname_url = cityname_url
        self.jobname_url = jobname_url

        self.citynname = cityname
        self.jobname = jobname
        self.url_start = "https://www.lagou.com/jobs/list_{}?px=default&city={}".format(jobname_url, cityname_url)
        self.url_parse = "https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false".format(cityname_url)
        self.headers = {
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Referer': 'https://www.lagou.com/jobs/list_{}?city={}&cl=false&fromSearch=true&labelWords=&suginput='.format(jobname_url, cityname_url),
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'

        }

    # 获取的cookies
    def pagecookie(self):
        s = requests.Session()
        # print(type(s))
        s.get(self.url_start, headers=self.headers, timeout=3)  # 请求首页获取cookies
        cookie = s.cookies  # 为此次获取的cookies
        return s, cookie

    # 請求,獲取響應
    def parse_url(self, url, s, cookie, page):
        data = {
            "first": "true",
            "pn": "{}".format(page),
            "kd": "{}".format(self.jobname)
        }
        response = s.post(url, data=data, headers=self.headers, cookies=cookie, timeout=3)  # 获取此次文本
        time.sleep(7)
        ret = response.content.decode()
        # 轉換成dict字典
        ret1 = json.loads(ret)
        return ret1

    # 組織新的json檔
    def newinfo(self, listinfo):
        final_dict = {}
        new_list = []
        # print(len(listinfo))
        # print(type(listinfo))
        for i in listinfo:
            new_dict = {}
            new_dict["createTime"] = i["createTime"]
            new_dict["companyFullName"] = i["companyFullName"]
            new_dict["companyShortName"] = i["companyShortName"]
            new_dict["positionName"] = i["positionName"]
            new_dict["workYear"] = i["workYear"]
            new_dict["education"] = i["education"]
            new_dict["jobNature"] = i["jobNature"]
            new_dict["salary"] = i["salary"]
            new_dict["companySize"] = i["companySize"]
            new_dict["industryField"] = i["industryField"]
            new_dict["positionAdvantage"] = i["positionAdvantage"]
            new_dict["companyLogo"] = i["companyLogo"]
            new_dict["city"] = i["city"]
            new_dict["district"] = i["district"]

            new_list.append(new_dict)
        final_dict["result"] = new_list
        return final_dict

    def save_dict(self, dict_json, page, listinfo):
        final_dict = self.newinfo(listinfo)
        file_name = "lagou拉勾求職信息/lagou求職信息({})_{}第{}頁.json".format(self.citynname, self.jobname, page)
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(json.dumps(final_dict, ensure_ascii=False, indent=2))

    def run(self):  # 主要實現邏輯
        # 獲取cookie
        s, cookie = self.pagecookie()
        # 1.構建url列表
        page = 1
        while page > 0:
            # 2.歷遍,請求,獲取響應
            dict_json = self.parse_url(self.url_parse, s, cookie, page)
            # list 列表
            nextinfo = dict_json["content"]["positionResult"]["result"]
            print(len(nextinfo))
            if len(nextinfo) > 0:
                # 3.保存
                self.save_dict(dict_json, page, nextinfo)
                page += 1
            else:
                page = 0


if __name__ == "__main__":
    lagouspider = LagouSpider("廣州", "python爬虫")
    lagouspider.run()
    # main()
