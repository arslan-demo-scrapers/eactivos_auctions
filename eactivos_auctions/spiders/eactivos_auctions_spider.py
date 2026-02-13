# -*- coding: utf-8 -*-
import json
import logging
import re
from copy import deepcopy

from scrapy import Request
from scrapy import Spider, FormRequest

from eactivos_auctions.eactivos_auctions.config.env_config import Config
from eactivos_auctions.eactivos_auctions.utils.clean_utils import clean, clean_seq, get_first, join_seq


class EactivosAuctionsSpider(Spider):
    name = "eactivos_spider"
    base_url = 'https://www.eactivos.com/'
    login_url = 'https://www.eactivos.com/login'
    auctions_url = 'https://www.eactivos.com/listado-de-liquidaciones.html'
    listings_url_t = 'https://www.eactivos.com/listado-de-liquidaciones/obtener?page={page_no}'
    next_page_url_t = 'https://www.eactivos.com/listado-de-liquidaciones/ver-mas?page={page_no}'
    bid_url_t = 'https://www.eactivos.com/liquidacion/{data_liquidation_id}/mejor-puja'

    end_date_re = re.compile(r'finaliza el(.*).')

    start_urls = [
        login_url,
    ]

    handle_httpstatus_list = [
        400, 401, 402, 403, 404, 405, 406, 407, 409,
        500, 501, 502, 503, 504, 505, 506, 507, 509,
    ]

    csv_headers = [
        'Auction_ID', 'Name', 'Location', 'Category', 'Appraisal_Amount', 'Auction_Value',
        'Minimum_Bid', 'Highest_Bid', 'Has_Started', 'Start_Date', 'End_Date', 'Finca', 'Registro',
        'Management_Costs', 'Expenses', 'Characteristics', 'Description', 'Complete_Description',
        'Image_Links', 'Document_Links', 'Downloaded_File_Paths', 'URL',
    ]

    feeds = {
        '../output/eactivos_auctions.csv': {
            'format': 'csv',
            'encoding': 'utf8',
            'store_empty': False,
            'fields': csv_headers,
            'indent': 4,
            'overwrite': True,
        }
    }

    custom_settings = {
        'FEEDS': feeds,
        'CONCURRENT_REQUESTS': 1,
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'cookie': 'PHPSESSID=106bbce025d95e27598797aca8b24bf5;',
        'Pragma': 'no-cache',
        'Referer': 'https://www.eactivos.com/listado-de-liquidaciones.html',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    }

    meta = {
        'handle_httpstatus_list': handle_httpstatus_list,
    }

    cookies = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse, headers=self.headers)

    def parse(self, response, **kwargs):
        self.get_request_cookies(response)

        data = {
            '_username': Config.EACTIVOS_LOGIN_EMAIL,
            '_password': Config.EACTIVOS_LOGIN_PASSWORD,
            '_csrf_token': self.get_form_token(response),
        }

        return FormRequest(url=self.login_url,
                           callback=self.parse_login,
                           headers=self.headers,
                           meta=self.meta,
                           formdata=data,
                           )

    def parse_login(self, response):
        meta = deepcopy(self.meta)
        meta['page_no'] = 1

        return response.follow(url=self.listings_url_t.format(**meta),
                               callback=self.parse_listings,
                               headers=self.headers,
                               dont_filter=True,
                               meta=meta,
                               )

    def parse_listings(self, response):
        if not response.css('.liquidation-card'):
            return

        for sel in response.css('.liquidation-card.card.px-0')[:]:
            item = {}
            item['Name'] = self.get_title(sel)
            item['Location'] = self.get_location(sel)
            item['URL'] = self.get_auction_url(response, sel)

            meta = deepcopy(self.meta)
            meta['item'] = item

            # url = 'subasta-del-50-de-finca-rustica-en-valdelaguna-madrid'
            # if url not in item['URL']:
            #     continue

            yield response.follow(url=item['URL'],
                                  callback=self.parse_auction_details,
                                  headers=self.headers,
                                  meta=meta,
                                  )

        if 'No hay liquidaciones disponibles' in response.text or not response.css('.liquidation-card.card.px-0'):
            return
        response.meta['page_no'] += 1

        yield response.follow(url=self.listings_url_t.format(**response.meta),
                              callback=self.parse_listings,
                              headers=self.headers,
                              meta=response.meta,
                              )

    def parse_auction_details(self, response):
        item = response.meta['item']
        item['Auction_ID'] = self.get_auction_id(response)
        item['Appraisal_Amount'] = self.get_appraisal_amount(response)
        item['Auction_Value'] = self.get_auction_value(response)
        item['Minimum_Bid'] = self.get_minimum_bid(response)
        item['Has_Started'] = self.has_started(response)
        item['Start_Date'] = ''
        item['End_Date'] = self.get_end_date(response)
        item['Category'] = self.get_category(response)
        item['Document_Links'] = self.get_document_links(response)
        item['Characteristics'] = self.get_characteristics(response)
        item['Management_Costs'] = self.get_management_cost(response)
        item['Expenses'] = self.get_expenses(response)
        item['Image_Links'] = self.get_image_urls(response)
        item['Description'] = self.get_description(response)
        item['Complete_Description'] = self.get_description_html(response)
        item['Registro'] = self.get_registro(response)
        item['Finca'] = self.get_finca(response)

        if not item['Has_Started']:
            item['Start_Date'] = item['End_Date']
            item['End_Date'] = ''

        if item['Location'] not in item['Name'] and ' en ' in item['Name']:
            item['Location'] = clean(item['Name'].split(' en ')[-1])

        item['headers'] = self.headers

        meta = deepcopy(self.meta)
        meta['item'] = item

        if not self.get_data_liguidation_id(response):
            return item
        bid_url = self.bid_url_t.format(data_liquidation_id=self.get_data_liguidation_id(response))
        return Request(url=bid_url, callback=self.parse_highest_bid, meta=meta, headers=self.headers)

    def parse_highest_bid(self, response):
        item = response.meta['item']

        try:
            data = json.loads(response.text)
            item['Highest_Bid'] = f"{data['amount'] or 0} €"
        except Exception as err:
            logging.error(err)

        return item

    def get_form_token(self, response):
        return response.css('[name="_csrf_token"]::attr(value)').get()

    def get_auction_url(self, response, sel):
        return response.urljoin(sel.css('a::attr(href)').get())

    def get_auction_id(self, response):
        return f"{response.url.split('/')[3]}_{self.get_data_liguidation_id(response)}"

    def get_appraisal_amount(self, response):
        return self.get_attribute_value(response, 'VALORACIÓN')

    def get_auction_value(self, response):
        return self.get_appraisal_amount(response)

    def get_title(self, response):
        return get_first(response.css('.card-title a::text').getall())

    def get_attribute_value(self, response, key, up_to_index=1):
        val1 = get_first(response.css(f'.text-label:contains("{key}") + .text-value::text').getall(), up_to_index)
        val2 = get_first(response.css(f'.text-label:contains("{key}") + .text-value ::text').getall(), up_to_index)
        return val1 or val2

    def get_minimum_bid(self, response):
        return clean(response.css('.current-bid-amount::text').get())

    def get_category(self, selector):
        return clean_seq(selector.css('.breadcrumb a::text').getall())[-1]

    def get_description_html(self, response):
        return response.css('#liquidation-tab-content, #tab-description').get()

    def get_location(self, sel):
        return get_first(sel.css('.card-subtitle.mb-3 ::text').getall())

    def has_started(self, response):
        # return 'Próximamente' not in response.text
        return 'finaliza el' in response.css('#end-date ::text').get('').lower()

    def get_end_date(self, response):
        return response.css('#countdown::attr(data-end-date)').get() or ''

    def get_start_date(self, response):
        return clean((self.end_date_re.findall(response.text) or [''])[0].split('.')[0])

    def get_description(self, response):
        return join_seq(response.css('#tab-description ::text').getall(), sep=" ")

    def get_document_links(self, response):
        return [response.urljoin(url) for url in
                response.css('a.documentation-link::attr(href)').getall()]

    def get_registro(self, response):
        return get_first(response.css('#tab-features p:contains("REGISTRO") + p::text').getall())

    def get_finca(self, response):
        return get_first(response.css('#tab-features p:contains("FINCA") + p::text').getall())

    def get_characteristics(self, response):
        return join_seq(response.css('#tab-features ::text').getall())

    def get_expenses(self, response):
        return join_seq(response.css('#tab-expenses-and-charges ::text').getall())

    def get_image_urls(self, response):
        return ",\n".join(response.urljoin(url) for url in response.css('#carousel img::attr(src)').getall())

    def get_management_cost(self, response):
        return "".join(self.get_attribute_value(response, 'GASTOS DE GESTIÓN').split()[:1])

    def get_data_liguidation_id(self, response):
        return response.css('::attr(data-liquidation)').get()

    def get_auction_data(self, response):
        try:
            return json.loads(response.css('[type="application/ld+json"]::text').get('{}'))
        except Exception as err:
            logging.error(err)

        return {}

    def get_request_cookies(self, response):
        ck = [str(cookies).split(';')[0][2:] for cookies in dict(response.headers)[b'Set-Cookie']]
        cookies = {c.split('=')[0]: '='.join(c.split('=')[1:]) for c in ck}
        self.cookies.update(cookies)
        self.headers['Cookie'] = self.get_str_cookie(cookies)
        return cookies

    def get_str_cookie(self, cookies):
        cookie = ''
        for k, v in cookies.items():
            cookie += f"{k}={v}; "
        return cookie.rstrip('; ')
