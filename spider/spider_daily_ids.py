# coding:utf-8
import requests
import logging
import json
import time
import settings
import traceback, sys
from datetime import date, timedelta

logging.basicConfig(level=logging.DEBUG, **settings.LOGGING_SPIDER)

base_header = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Host": "www.erlangcha.com",
    "Referer": "https://www.erlangcha.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

products = ["445282",
            "392224",
            "359071",
            "447122",
            "418898",
            "284367",
            "432838",
            "403914",
            "366281",
            "261557",
            "336828",
            "447927",
            "392322",
            "385069",
            "467372",
            "202325",
            "303040",
            "431260",
            "429342",
            "346328",
            "321576",
            "224972",
            "327671",
            "440634",
            "396291",
            "339051",
            "451872",
            "413800",
            "231335",
            "463296",
            "403412",
            "251983",
            "444435",
            "343248",
            "470687",
            "364172",
            "273377",
            "239878",
            "203745",
            "451564",
            "390422",
            "350521",
            "434571",
            "295083",
            "261825",
            "414214",
            "397859",
            "295459",
            "393783",
            "287207", ]


class SpiderDailyProducts(object):
    """
    抓取每日更新的商品
    """

    def __init__(self):
        self.elc_home_url = "https://www.erlangcha.com/"
        self.elc_date_base_url = "https://www.erlangcha.com/data/get?page={}&limit=200&search_name=&start_date={}&end_date={}&topType=&secType=&store_name=&field=today_volume&order=desc"
        self.save_data_api = "http://47.103.69.161:9020/insert/product-info"
        self.session = requests.Session()

    def set_cookie(self, session_cookie):
        """设置cookie"""
        cookies_dict = requests.utils.dict_from_cookiejar(session_cookie)
        base_header["Cookie"] = json.dumps(cookies_dict)

    def save_data(self, datas):
        """保存数据"""
        try:
            for data in datas:
                if data.get("store"):
                    store = data.get("store")
                else:
                    store = data.get("Store")

                save_data = {
                    "product_id": data.get("id"),
                    "product_code": data.get("product_code"),
                    "status": 0,
                    "product_link": data.get("shop_link") if data.get("shop_link") else "-",
                    "product_title": data.get("shop_title") if data.get("shop_title") else "-",
                    "product_img": data.get("shop_img") if data.get("shop_img") else "-",
                    "online_time": data.get("online_time") if data.get("online_time") else "-",
                    "today_sales": int(data.get("today_volume")) if data.get("today_volume") else 0,
                    # "three_volume": data.get("three_total") if data.get("three_total") else "-",
                    # "seven_volume": data.get("seven_total") if data.get("seven_total") else "-",
                    "total_sales": int(data.get("sales_volume")) if data.get("sales_volume") else 0,
                    "price": float(data.get("price")) if data.get("price") else 0,
                    # "price_max": data.get("price_max") if data.get("price_max") else "-",
                    "product_created_at": data.get("created_at") if data.get("created_at") else "-",
                    "product_updated_at": data.get("updated_at") if data.get("updated_at") else "-",
                    "first_type": data.get("top_type").get("type_name") if data.get(
                        "top_type") is not None else "-",
                    "second_type": data.get("type").get("type_name") if data.get(
                        "type") is not None else "-",
                    "shop_name": store.get("name") if store else "-",
                    "shop_code": store.get("code") if store else "-",
                    "shop_link": store.get("link") if store else "-",
                    "shop_logo": store.get("logo") if store else "-",
                    "shop_created_at": store.get("created_at") if store else "-",
                    "shop_updated_at": store.get("updated_at") if store else "-",
                    "date": time.strftime("%Y-%m-%d", time.localtime()),
                }

                resp = requests.post(self.save_data_api, data=json.dumps(save_data))
                logging.info("product code:{},{}".format(data.get("product_code"), resp.text))
                print("product code:{},{}".format(data.get("product_code"), resp.text))
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = str(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))  # 将异常信息转为字符串
            logging.error("save_data error:{}".format(error))

    def spider(self):
        try:
            resp = self.session.get(self.elc_home_url, headers=base_header)
            if resp.text == 403 or resp.text == "403":
                logging.critical("The ip is blocked.")
                return
            self.set_cookie(self.session.cookies)
            yesterday = date.today() + timedelta(days=-1)
            today = time.strftime("%Y-%m-%d", time.localtime())

            page_num = 1
            while True:
                resp = self.session.get(self.elc_date_base_url.format(page_num, yesterday, today),
                                        headers=base_header)
                if resp.text == 403 or resp.text == "403":
                    logging.critical("The ip is blocked.")
                    return
                info_json = json.loads(resp.text)
                if info_json and info_json.get("data"):
                    data_list = info_json["data"]
                    if len(data_list) == 0:
                        break
                    self.save_data(data_list)
                page_num += 1
            logging.info("Spider Done!", time.strftime("%Y-%m-%d", time.localtime()))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = str(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))  # 将异常信息转为字符串
            logging.error("Spider error:{}".format(error))


if __name__ == '__main__':
    spider = SpiderDailyProducts()
    spider.spider()
