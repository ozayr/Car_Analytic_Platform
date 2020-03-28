# -*- coding: utf-8 -*-
import scrapy
from lxml import html
import json
from datetime import datetime
import re


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def remove_junk(val):
    if ':' in val:
        return val[1:].strip()
    else:
        return val

def get_deriv(val):
    return " ".join(val.split()[3:])


body_types = ['Hatch', 'sedan', 'coupe', 'double cab','cabriolet']
def get_body(val):
    b_t = [body for body in body_types if body in val]
    return b_t[0] if b_t else 'N/A'


class DriverSpider(scrapy.Spider):
    name = 'driver'
    allowed_domains = ['driveit.co.za']


    custom_settings = {
        'FEED_URI':'../json_data_files/driveit{}.json'.format(datetime.strftime(datetime.today(), '_%Y%m%d_%M')),
        'FEED_FORMAT': 'json'
    }

    car_dict = dict()

    def start_requests(self):
        url = 'https://www.driveit.co.za/cars-for-sale/?per_page=15'
        yield scrapy.Request(url )

    def parse(self, response):
        # return {'Response':response.text}
        tree = html.fromstring(response.text )

        try:
            ID = tree.xpath('//li[contains(@class,"spot-item border-color-input")]/@id')

            title = tree.xpath('//li[contains(@class,"spot-item border-color-input")]//a[@class="spot-image"]/@title')
            url = tree.xpath('//li[contains(@class,"spot-item border-color-input")]//a[@class="spot-image"]/@href')

            info = tree.xpath('//li[contains(@class,"spot-item border-color-input")]//ul[@class="spot-search-fields"]//li/text()')
            info = list(map(remove_junk, info))
            info = list(divide_chunks(info, 8))
            make, model, location, mileage, year, fuel, transmission, color = map(list, zip(*info))
            price = tree.xpath('//li[contains(@class,"spot-item border-color-input")]//ul[@class="spot-search-fields"]//li/span[@class="big"]/text()')

            capacity = [re.findall("\d+\.\d+|\d+\.\d+\D+", phrase)[0] if re.findall("\d+\.\d+|\d+\.\d+\D+", phrase) else 'N/A' for phrase in title]


            body = list(map(get_body, title))
            deriviative = list(map(get_deriv, title))

            driveit = {index: {'year': y,
                               'make': mk,
                               'model': m,
                               'deriviative': d,
                               'mileage': ml,
                               'price': p,
                               'engine': c,
                               'fuel': f,
                               'body': b,
                               'transmision': trans,
                               'url': u,
                               'location': loc,
                               'date': datetime.strftime(datetime.today(), '%Y-%m-%d'),
                               'title': t}
                       for index, y, mk, m, d, ml, p, c, f, b, trans, u, loc, t in zip(ID, year, make, model, deriviative, mileage, price, capacity, fuel, body, transmission, url,location, title )}
        except:
            driveit = {}

        self.car_dict = {**self.car_dict,**driveit}
        next_page_url = tree.xpath('//li/a[text()="next"]/@href')
        if next_page_url :
            print('scraping: ', next_page_url )
            yield scrapy.Request(next_page_url[0],callback = self.parse)
        else:
            yield self.car_dict

