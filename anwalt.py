import time
from playwright.sync_api import sync_playwright
import scrapy
import csv
from argparse import ArgumentParser


def parse(response,writer):
    sel = scrapy.Selector(text=response)
    for res in sel.xpath("//div[@class='anw-hover-border']"):
        name = res.xpath("./div/a/@title").get()
        print(name)
        name = " ".join(name.split(" ")[1:])
        print(name)
        temp = name.split(" ") # Mag. René Fischer
        first = temp[-2]
        last = temp[-1]
        if '.' in temp[0]:
            dr = temp[0].replace('.','')
        else:
            dr = ''
        addr = res.xpath("./div[@class='mb-3 small']//text()").getall()
        addr.pop(-1)
        addr = [a for a in addr if a.strip()]     
        comapny = addr[0]       
        three = addr[1].split(',')
        street_address = three[0]
        temp = three[1].strip().split(' ')
        postal = temp[0]
        city = " ".join(temp[1:])
        country = three[-1]
        # # pprint([dr,first,last,comapny,street_address,postal,city,country],expand_all=True)
        writer.writerow([dr,first,last,comapny,street_address,postal,city,country])

def driver(writer):
    print(" [+] Started")
    play = sync_playwright().start()
    browser = play.chromium.launch(headless=False)
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36")
    page = context.new_page()
    urls = []
    with open("urls.txt",'r') as f:
        raw_urls = f.readlines()
        for url in raw_urls:
            url = url.strip().replace('\n','')
            urls.append(url)
    for url in urls:
        page.goto(url)
        try:
            print(" [+] Just Wait a sec!")
            page.wait_for_selector("//div[@id='CybotCookiebotDialog']",timeout=5000)
            page.locator("//a[@id='CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll']").click()
        except:
            pass
        page.locator("//a[@class='btn btn-outline-dark px-4' and contains(@href, 'https')]").click()
        down = page.locator("//div[@class='container-fluid bg-light']")
        box = down.bounding_box()
        if box:
            y = box.get('y')
            page.mouse.wheel(0,y)
        while True:
            sel = scrapy.Selector(text=page.content())
            previous = len(sel.xpath("//a[@class='stretched-link anw-plain']/@href").getall())
            print("\r [+] Extracting data..",end='')
            down = page.locator("//div[@class='container-fluid bg-light']")
            box = down.bounding_box()
            if box:
                # it will get the location of element vertically
                y = box.get('y')
                # (x,y)
                # here we can pass custom values as well to scroll as we want
                page.mouse.wheel(0,y)
                time.sleep(5)
            sel = scrapy.Selector(text=page.content())
            current = len(sel.xpath("//a[@class='stretched-link anw-plain']/@href").getall())
            if previous == current:
                parse(page.content(),writer)
                break
            else:
                continue
        print(" [+] Finished")
        play.stop()

parser = ArgumentParser()
parser.add_argument('-o','--output',dest='output_file',help='give output filename') 
values = parser.parse_args()  # it only return value object , while optparse return both value obj and arguments obj.
args_dict = vars(values) # will return dict of given object
if args_dict.get("output_file"):
    filename = args_dict.get("output_file")
else:
    filename = 'result.csv'
file = open(filename,'w')
writer = csv.writer(file)
writer.writerow(['#','First_Name','Last_Name','Comapany','Street_Address','Postal','City','Country'])
driver(writer)