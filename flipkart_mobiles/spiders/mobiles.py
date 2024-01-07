import scrapy
import json
from urllib.parse import urljoin
import re
import urllib.request


class MobilesSpider(scrapy.Spider):
    name = "mobiles"
    # allowed_domains = ["flipkart.com"]
    # start_urls = ["https://www.flipkart.com/mobiles/pr?sid=4io"]

    def start_requests(self):
         category_list = ['4io']
         for category in category_list:
            flipkart_search_url = f"https://www.flipkart.com/mobiles/pr?sid={category}&page=1"
            yield scrapy.Request(url=flipkart_search_url, callback=self.discover_product_urls, meta={'category': category, 'page': 1})

    def discover_product_urls(self, response):

        # retry_count = response.meta['retry_count']
        page = response.meta['page']
        category = response.meta['category']

        ## Discover Product URLs
        products = response.css("._3Mn1Gg *._4ddWXP")
        # self.log(f"Found {len(products)} products on the page")

        for product in products:
            relative_url = product.css("a.s1Q9rs::attr(href)").get().split("&")[0]
            product_url = urljoin('https://www.flipkart.com', relative_url)
            yield scrapy.Request(url=product_url, callback=self.parse_product_data, meta={'category': category, 'page': page})


        ## Get Next Page Url
        next_page_relative_url = response.css(".yFHi8N a:last-child::attr(href)").get()
        if next_page_relative_url is not None:
            next_page = urljoin('https://www.flipkart.com/', next_page_relative_url)
            yield scrapy.Request(url=next_page, callback=self.discover_product_urls)


        
        # ## Get All Pages
        # if page == 1:
        #     # available_pages = response.xpath('//div[@class="_2MImiq"]/span/text()').get().split()[-1]
        #     available_pages = response.css('div._2MImiq span::text').get().split()[-1]

        #     last_page = available_pages[-1]
        #     for page_num in range(2, int(last_page)):
        #         flipkart_search_url = f"https://www.flipkart.com/mobiles/pr?sid={category}&page={page_num}"
        #         yield scrapy.Request(url=flipkart_search_url, callback=self.discover_product_urls, meta={'category': category, 'page': page_num})


    def parse_product_data(self, response):
        
        # image_url = ''.join(response.css(".CXW8mj img ::attr(src)").get().removesuffix("?q=70").split("416/416/"))
        image_urls = []
        for url in response.css("._3GnUWp li img::attr(src)").getall():
            image_url = ''.join(url.removesuffix("?q=70").split("128/128/"))
            image_urls.append(image_url)

        highlights = [bullet.strip() for bullet in response.css("._2418kt li ::text").getall()]

        yield {
            "Images": image_urls,
            "Product-Name": response.css(".B_NuCI ::text").get().strip(),
            "Selling-Price": response.css('._30jeq3 ::text').get(),
            "MRP": ''.join(response.css('div._3I9_wc._2p6lqe ::text').getall()),
            "Rating-Star": f"{response.css("._3LWZlK ::text").get("").strip()} out of 5",
            "Rating_Count": response.css("._2_R_DZ>span ::text").get("").strip(),
            "Highlights": highlights,
        }
