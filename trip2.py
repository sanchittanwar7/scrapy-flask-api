# -*- coding: utf-8 -*-
import scrapy
import requests


class Trip2Spider(scrapy.Spider):
	name = 'trip2'
	allowed_domains = ['tripadvisor.in']

	def __init__(self, location, reviews_list, *args, **kwargs):
		self.reviews_list = reviews_list
		super(Trip2Spider, self).__init__(*args, **kwargs)
		self.location = location
		self.query = ''
		self.start_url = "https://www.tripadvisor.com/TypeAheadJson?action=API&types=geonbrhdhoteltheme_park&filter=&legacy_format=true&urlList=true&strictParent=true&query=%s&max=6&name_depth=3&interleaved=true&scoreThreshold=0.5&strictAnd=false&typeahead1_5=true&disableMaxGroupSize=true&geoBoostFix=true&geoPages=&injectList=&neighborhood_geos=true&details=true&rescue=true&uiOrigin=trip_search_Hotels&source=trip_search_Hotels"
		self.sno = 0
		self.custom_url = ''

	def start_requests(self):
		url = self.start_url % self.location
		r = requests.get(url=url)
		r = r.json()
		s = r[0]['url'][8:].split('-')
		self.url = ("https://www.tripadvisor.in/Attractions-" + str(s[1]) + "-%sActivities-" + str(s[2]))
		initial_url = ("https://www.tripadvisor.in/Attractions-" + str(s[1]) + "-%sActivities-" + str(s[2])) % ''
		print(initial_url)
		yield scrapy.Request(initial_url, callback=self.parse_page)

	def parse_page(self, response):
		urls = response.css('div.listing_title > a::attr(href)').extract()
		for url in urls:
			url = 'https://www.tripadvisor.in' + url
			try:
				self.custom_url = url.split('Reviews')[0] + 'Reviews%s' + url.split('Reviews')[1]
			except (IndexError):
				continue
			yield scrapy.Request(url=url, callback=self.parse_reviews)
		# self.sno += 30
		# self.query = 'oa%s-' % self.sno
		# url = self.url % (self.query)
		# yield scrapy.Request(url, callback=self.parse_page)

	def parse_reviews(self, response):
		reviews = response.css('div.review-container')
		print("------------------------------------------------------")
		print(response.css('h1#HEADING::text').extract_first())
		print("------------------------------------------------------")
		for review in reviews:
			yield{
			'hotel_name': response.css('h1#HEADING::text').extract_first(),
			'user_name' : review.css('div.info_text > div::text').extract_first(),
			'user_contribution' : review.css('span.badgetext::text').extract_first(),
			'heading' : review.css('span.noQuotes::text').extract_first(),
			'review' : review.css('p.partial_entry::text').extract_first()
			}
			self.reviews_list.append({
				'place_name': response.css('h1#HEADING::text').extract_first(),
				'user_name' : review.css('div.info_text > div::text').extract_first(),
				'user_contribution' : review.css('span.badgetext::text').extract_first(),
				'heading' : review.css('span.noQuotes::text').extract_first(),
				'review' : review.css('p.partial_entry::text').extract_first()
			})
		# offset = response.css('a.next::attr(data-offset)').extract_first()
		# if offset != None:
		# 	print(offset)
		# 	next_page_url = self.custom_url % ('-or%s' % offset)
		# 	print(next_page_url)
		# 	yield scrapy.Request(url=next_page_url, callback=self.parse_reviews)









