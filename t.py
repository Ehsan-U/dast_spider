from http.server import executable
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

g_repo = set()

def fetch(writer):
    opt = Options()
    driver = Chrome(executable_path="chromedriver.exe")
    urls = []
    with open("urls.txt",'r') as f:
        raw_urls = f.readlines()
        for url in raw_urls: 
            if url:
                url = url.strip('\n')
                urls.append(url) 
    for url in urls:
        driver.get(url)
        try:
            WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,"//div[@id='mkc-manager']")))
        except:
            pass
        else:
            driver.find_element(by=By.XPATH,value="//button[@id='mkc-btn-select-all']").click()
        while True:
            try:
                # window.scrollTo(0, document.body.scrollHeight);
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,"//button[@id='more_btn']")))
            except:
                input("e:")
                print(" [+] Not found")
                break
            else:
                source = driver.page_source
                parse(source,writer)
                input("e:")
                driver.find_element(by=By.XPATH,value="//button[@id='more_btn']").click()
                print(" [+] Looping..")
                continue
    driver.close()

def parse(response,writer):
    sel = Selector(text=response)
    for res in sel.xpath("//table[@id='table-searchresult']"):
        name = res.xpath("./tbody/tr/td[2]/div/div[1]//text()").get()
        email = res.xpath("./tbody/tr//i[@class='fas fa-envelope']/following-sibling::a/text()").get()
        address = res.xpath("./tbody/tr//i[@class='fas fa-map-marker']/parent::div/text()").get()
        if not name in g_repo and not email in g_repo and not address in g_repo:
            print(name,email,address)
            writer.writerow([name,email,address])

if __name__ == "__main__":
    filename = open("result.csv",'w',encoding='utf-8')
    writer = csv.writer(filename)
    writer.writerow(['Name','Email','Address'])
    fetch(writer)
    filename.close()
