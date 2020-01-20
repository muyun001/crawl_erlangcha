# coding: utf-8

from spider.spider_daily_ids import SpiderDailyProducts


def run_daily_spider():
    spider = SpiderDailyProducts()
    spider.spider()


if __name__ == '__main__':
    run_daily_spider()
