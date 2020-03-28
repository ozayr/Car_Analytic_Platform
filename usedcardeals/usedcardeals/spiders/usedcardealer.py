# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from lxml import html
import re


def get_deriv(val):
    return " ".join(val.split()[1:])


def get_model(val):
    return val.split()[0]


def striper_intify(val):
    return int(re.sub('[R\s,]', '', val.strip()))


def intify_mileage(val):
    return int(re.sub('[km,]', '', val))


class UsedcardealerSpider(scrapy.Spider):
    name = 'usedcardealer'
    allowed_domains = ['usedcardeals.co.za']
    base_url = 'http://www.usedcardeals.co.za'
    custom_settings = {
        'FEED_URI': '../json_data_files/usedcardeals{}.json'.format(datetime.strftime(datetime.today(), '_%Y%m%d_%M')),
        'FEED_FORMAT': 'json'
    }
    car_dict = dict()

    def start_requests(self):
        url = 'http://www.usedcardeals.co.za/search-result/?start=0'
        yield scrapy.Request(url)

    def parse(self, response):
        # return {'Response': response.text}
        tree = html.fromstring(response.text)
        try:
            ID = tree.xpath('//div[contains(@class,"vehicle-list-block")]/@data-vehicleid')
            make = tree.xpath('//div[contains(@class,"vehicle-list-block")]/@data-make')

            model_dir = tree.xpath('//div[contains(@class,"vehicle-list-block")]/@data-model')
            model = list(map(get_model, model_dir))

            deriviative = list(map(get_deriv, model_dir))
            capacity = [
                re.findall("\d+\.\d+|\d+\.\d+\D+", phrase)[0] if re.findall("\d+\.\d+|\d+\.\d+\D+", phrase) else 'N/A'
                for phrase in deriviative]
            year = list(map(int, tree.xpath('//div[contains(@class,"vehicle-list-block")]/@data-year')))
            mileage = tree.xpath('//div[contains(@class,"vehicle-list-block")]/@data-mileage')
            mileage = list(map(intify_mileage, mileage))
            price = tree.xpath('//div[contains(@class,"vehicle-list-block")]/@data-price')
            price = list(map(striper_intify, price))
            url = tree.xpath('//div[contains(@class,"vehicle-list-block")]/@data-detailurl')

            usedcardeals = {
                index: {'year': y, 'make': mk, 'model': m, 'deriviative': d, 'mileage': ml, 'price': p, 'engine': c,
                        'url': u, 'date': datetime.strftime(datetime.today(), '%Y-%m-%d')}
                for index, y, mk, m, d, ml, p, c, u in
                zip(ID, year, make, model, deriviative, mileage, price, capacity, url)}
        except:
            usedcardeals = {}

        self.car_dict = {**self.car_dict, **usedcardeals}

        next_page_extension = tree.xpath('//div[@class="pagination"]/ul/li[12]/a/@href')[0]
        print(next_page_extension)
        if next_page_extension != '#':
            next_page_url = ''.join([self.base_url, next_page_extension])
            print('scraping: ', next_page_url)
            yield scrapy.Request(next_page_url, callback=self.parse)
        else:
            yield self.car_dict
