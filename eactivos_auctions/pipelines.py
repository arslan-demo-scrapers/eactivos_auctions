# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import os
from urllib.parse import urlparse

from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from scrapy.spiders import Request

from eactivos_auctions.eactivos_auctions.database.db_operations import DBOperations


class EactivosAuctionsFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        path = f'{request.meta["Auction_ID"]}/{request.meta["Index"]}_{os.path.basename(urlparse(request.url).path)}'
        if '.pdf' not in path:
            path += '.pdf'
        return path

    def get_media_requests(self, item, info):
        for i, url in enumerate(item['Document_Links'], start=1):
            yield Request(url, meta={'Auction_ID': item['Auction_ID'], 'Index': i}, headers=item['headers'])

    def item_completed(self, results, item, info):
        paths = ['files/' + x['path'] for ok, x in results if ok]
        if not paths:
            # raise DropItem("Item contains no images")
            item['Downloaded_File_Paths'] = ''
            return item

        adapter = ItemAdapter(item)
        adapter['Downloaded_File_Paths'] = ",\n".join(paths)
        return item


class EactivosAuctionsDatabasePipeline:
    db = DBOperations()

    def process_item(self, item, spider):
        item.pop('headers', {})
        item['Document_Links'] = ",\n".join(item['Document_Links'])
        self.db.insert_auction_db(item)
        return item


class EactivosAuctionsPipeline:
    def process_item(self, item, spider):
        return item
