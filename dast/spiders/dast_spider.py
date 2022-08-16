import scrapy
from scrapy_playwright.page import PageMethod


class DastSpiderSpider(scrapy.Spider):
    name = 'dast_spider'
    allowed_domains = ['dastelefonbuch.de']
    i = 0

    def start_requests(self):
        urls = []
        with open("spiders/urls.txt",'r') as f:
            raw_urls = f.readlines()
            for url in raw_urls:
                url = url.strip()
                url = url.replace("\n",'')
                urls.append(url)
        for url in urls:
            yield scrapy.Request(url,callback=self.parse,meta={
                "playwright":True,
                "playwright_include_page":True,
                "playwright_context":'new',
                'playwright_page_methods':[
                    PageMethod("wait_for_selector","//div[@id='entry_1']"),
                    PageMethod('evaluate','window.scrollBy(0, document.body.scrollHeight)'),
                    PageMethod('wait_for_selector',"//a[@class='btn blight']")
                ]
            })

    async def parse(self, response):
        print(" [+] Started")
        page = response.meta.get("playwright_page")
        sel = scrapy.Selector(text=response.text)
        await page.close()
        for res in sel.xpath("//div[@class='vcard']"):
            name,street_addr,postal,locality = None,None,None,None
            name = res.xpath("./div/@title").get()
            addr = res.xpath(".//a[@class='addr']/@title").get()
            if ',' in addr:
                addr = addr.split(",")
                if len(addr) > 1:
                    street_addr = addr[0]
                    temp = addr[1].strip().split(' ')
                    postal = temp[0]
                    locality = temp[1]
            else:
                temp = addr.strip().split(' ')
                postal = temp[0]
                locality = temp[1]
            self.i +=1
            print(f"\r [+] Extracted items: {i}",end='')
            yield {"Name":name,"Street_Address":street_addr,"Postal":postal,"Locality":locality}
        print(" [+] Finished")


            
