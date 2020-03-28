# -*- coding: utf-8 -*-
import scrapy
from lxml import html
from datetime import datetime
import string

provinces = ['western-cape' ,'eastern-cape','northern-Cape', 'north-west', 'free-state', 'kwazulu-natal', 'gauteng', 'limpopo' , 'mpumalanga']

def filter_ids(val):
    return 'used-cars' in val.split('/')

def get_id(val):
    return val.split('/')[-1]

def get_loc(val):
    search_string = val.split('/')[-2]
    return [loc for loc in provinces if loc in search_string]
def rm_spaces(val):
        return val.strip()

def rm_junk(val):
    return val.replace('\xa0', " ")

def split_info(val):
    return val.split(" ")


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_float(input_string):
    ignore_list = string.ascii_letters
    floats = []
    i = 0
    while i <len(input_string):
        temp = ""
        while input_string[i] not in ignore_list:
            temp+= input_string[i]
        if temp not in [" ",""]:
            floats.append(temp)



class CarshopperSpider(scrapy.Spider):
    name = 'carshopper'
    allowed_domains = ['carshop.co.za']
    base_url = 'https://www.carshop.co.za'
    custom_settings = {
        'FEED_URI':'../json_data_files/carshopper{}.json'.format(datetime.strftime(datetime.today(),'_%Y%m%d_%M')   ),
        'FEED_FORMAT':'json'
    }

    car_dict = dict()
    def start_requests(self):
        url = 'https://www.carshop.co.za/used-cars?page=1'
        yield scrapy.Request(url)

    count = 0
    def parse(self, response):

        tree = html.fromstring( response.text )
        try:
            url = tree.xpath('//div[@class = "VehicleViewBox"]/a/@href')
            url = list(filter(filter_ids, url))
            location = list(map(get_loc, url))
            ID = list(map(get_id, url))

            year_make_model = tree.xpath('//p[@class="VehicleTextArchive"]/text()')
            year_make_model = list(map(rm_spaces, year_make_model))
            year_make_model = list(filter(None, year_make_model))  # fastest
            year_make_model = list(map(rm_junk, year_make_model))
            year_make_model = list(map(split_info, year_make_model))
            year = [value[0] for value in year_make_model]
            make = [value[1] for value in year_make_model]
            model = [" ".join(value[2:]) for value in year_make_model]

            deriviative_mileage = tree.xpath('//strong/text()')
            deriviative_mileage = list(divide_chunks(deriviative_mileage, 2))
            deriviative,mileage = map(list, zip(*deriviative_mileage))


            price = tree.xpath('//span[@class="DealershipNameLeft"]/text()')

            capacity_fuel_body_transmission = tree.xpath('//td/p/text()')

            capacity_fuel_body_transmission = list(map(rm_spaces, capacity_fuel_body_transmission))

            capacity_fuel_body_transmission = list(divide_chunks(capacity_fuel_body_transmission, 5))

            capacity,fuel,body,transmission,_= map(list, zip(*capacity_fuel_body_transmission))

            carshop = {index: {'year': y, 'make': mk, 'model': m, 'deriviative': d, 'mileage': ml, 'price': p, 'engine': c,
                               'fuel': f, 'body': b, 'transmision': trans, 'url': u, 'location': loc,
                               'date': datetime.strftime(datetime.today(), '%Y-%m-%d')}
                       for index, y, mk, m, d, ml, p, c, f, b, trans, u, loc in
                       zip(ID, year, make, model, deriviative, mileage, price, capacity, fuel, body, transmission, url,
                           location)}

            for key in carshop.keys():
                if carshop[key]['engine'] == 'N/A':
                    carshop[key]['engine'] = [float(value) for value in carshop[key]['deriviative'].split() if
                                              ('.' in value)]
                    carshop[key]['engine'] = carshop[key]['engine'][0] if carshop[key]['engine'] else 'N/A'
        except Exception as e:
            carshop = {}
            print(e)

        self.car_dict = {**self.car_dict, **carshop}

        next_page_extension = tree.xpath('//li[@class="PagedList-skipToNext"]/a/@href')
        if next_page_extension:

            next_page_url = ''.join([self.base_url, next_page_extension[0]])
            print('scraping: ', next_page_url)
            yield scrapy.Request(next_page_url, callback=self.parse)
        else:
            yield self.car_dict