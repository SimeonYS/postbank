import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import PostbankItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class PostbankSpider(scrapy.Spider):
	name = 'postbank'
	start_urls = ['https://mediacenter.postbank.bg/category/news/']

	def parse(self, response):
		news = response.xpath('//div[@class="news"]')
		for new in news:
			date = new.xpath('.//div[@class="date"]/text()').get()
			date = re.findall(r'\d+\s\w+\s\d+',date)
			post_links = new.xpath('.//h2/a/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

		next_page = response.xpath('//li/a[@class="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response,date):

		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="content_left"]//text()[not (ancestor::h1) or (ancestor::div[@id="ssba"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=PostbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
