import requests
import csv
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector

def fetch(writer):
    opt = Options()
    
    s = Service(ChromeDriverManager().install())
    driver = Chrome(service=s)
    urls = []
    with open("urls.txt",'r') as f:
        raw_urls = f.readlines()
        for url in raw_urls: 
            if url:
                url = url.strip('\n')
                urls.append(url) 
    for url in urls:
        driver.get(url)
        while True:
            try:
                driver.find_element("//button[@id='more_btn']").click()
                WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[@id='more_btn']")))
            except:
                break
            else:
                source = driver.page_source
                parse(source,writer)
                continue
    driver.close()

def parse(response,writer):
    sel = Selector(text=response)
    for res in sel.xpath("//table[@id='table-searchresult']"):
        name = res.xpath("./tbody/tr/td[2]/div/div[1]//text()").get()
        email = res.xpath("./tbody/tr//i[@class='fas fa-envelope']/following-sibling::a/text()").get()
        address = res.xpath("./tbody/tr//i[@class='fas fa-map-marker']/parent::div/text()").get()
        writer.writerow([name,email,address])


filename = open("result.csv",'w',encoding='utf-8')
writer = csv.writer(filename)
writer.writerow(['Name','Email','Address'])
fetch(writer)
filename.close()