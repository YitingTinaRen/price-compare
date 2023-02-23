import time
import json
import random
import requests
import os
import boto3
from botocore.exceptions import ClientError
from urllib import parse
from bs4 import BeautifulSoup
import re


def lambda_handler(event, context):
    # TODO implement
    momo_spider = MomoSpider()

    Category=json.loads(event['Records'][0]['body'])
    print(f'Category is {Category}')
    print(f'Category  code is {Category["Code"]}')
    url = f"https://m.momoshop.com.tw/cateGoods.momo?cn={Category['Code']}&sourcePageType=4"
    result=momo_spider.get_products(url)
    print(f' Send to SQS: {result}')
    momo_spider.send2SQS(result['content'])


    return {
        'statusCode': 200,
        'body': json.dumps('pchome category crawling is successfull!')
    }


class MomoSpider():
    """Momo線上購物 爬蟲"""

    def __init__(self):
        self.post_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://m.momoshop.com.tw',
            'Referer': 'https://m.momoshop.com.tw/',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
        }
        self.get_headers1 = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        self.get_headers2 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }
        self.get_headers3 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
        }
        self.home_url = 'https://m.momoshop.com.tw/'

    def request_get(self, url, params=None):
        """送出 GET 請求

        :param url: 請求網址
        :param params: 傳遞參數資料
        :param to_json: 是否要轉為 JSON 格式
        :return data: requests 回應資料
        """
        # 用亂數去切換每次request的user agent來增加爬蟲成功率
        list4rand = [1, 2, 3]
        randNum = random.choice(list4rand)
        if randNum == 1:
            r = requests.get(url, params, headers=self.get_headers1)
        elif randNum == 2:
            r = requests.get(url, params, headers=self.get_headers2)
        else:
            r = requests.get(url, params, headers=self.get_headers3)

        if r.status_code != requests.codes.ok:
            print(f'網頁載入發生問題：{url}')

        try:
            r.encoding = 'UTF-8'
            data = BeautifulSoup(r.text, 'html.parser')
        except Exception as e:
            print(e)
            return None
        return data

    def request_post(self, url, payload=None):
        """送出 POST 請求

        :param url: 請求網址
        :param params: 傳遞參數資料
        :param to_json: 是否要轉為 JSON 格式
        :return data: requests 回應資料
        """
        s = requests.Session()
        surl = 'https://m.momoshop.com.tw/main.momo'

        list4rand = [1, 2, 3]
        randNum = random.choice(list4rand)
        if randNum == 1:
            r = requests.get(surl, headers=self.get_headers1)
        elif randNum == 2:
            r = requests.get(surl, headers=self.get_headers2)
        else:
            r = requests.get(surl, headers=self.get_headers3)

        r = requests.post(url, data=payload, headers=self.post_headers)

        if r.status_code != requests.codes.ok:
            print(f'網頁載入發生問題：{url}')
        try:
            data = r.text
        except Exception as e:
            print(e)
            return None
        return data

   
    def get_products(self, url):
        data = self.request_get(url)
        if data:
            if data.find(class_="classificationArea jsCategoryList"):
                print(
                    f'\n----------\nURL:{url}\n Not a bottom category!\n----------\n')
                return {'isProd': False, 'content': {}}
            else:
                print("No further category, collecting product info!")
                if not data.find(class_="prdListArea"):
                    print(
                        f'\n----------\nURL:{url}\n No product!\n----------\n')
                    return {'isProd': False, 'content': {}}

                PrdList_html = data.find(
                    class_="prdListArea").ul.find_all('li')

                Products = []
                for element in PrdList_html:
                    Prd_ID = element.find(id="goodsCode")['value']
                    Prd_Name = element.find(class_="productInfo")['title']
                    Prd_URL = element.find(class_="productInfo")['href']
                    Prd_Event = element.find(class_="prdEvent").getText()
                    Prd_Price = element.find(class_="priceArea").b.getText()
                    Prd_Image = []
                    for imgLink in element.find_all(
                            class_="goodsImg lazy lazy-loaded"):
                        Prd_Image.append(imgLink['src'])

                    Prod = {
                        'Id': Prd_ID,
                        'Name': Prd_Name,
                        'Url': Prd_URL,
                        'Event': Prd_Event,
                        'Price': int(Prd_Price.replace(',', '')),
                        'Pic': Prd_Image
                    }
                    Products.append(Prod)

                # Handle Product SaleCounts
                ProdIdList = [sub['Id'] for sub in Products]
                # print(ProdIdList)
                saleCount = self.get_sale_counts(ProdIdList)
                for key in list(saleCount.keys()):
                    # print(key)
                    Products[ProdIdList.index(key)].update(
                        {'Salecount': saleCount[key]})
                    # print(Products[ProdIdList.index(key)])

                # Handle next page
                # Find maxPage
                pattern = re.compile('var _maxPage =\"\d+\";')
                scriptTag = data.find_all("script", text=pattern)
                jsscript = scriptTag[0].string
                maxPageString = pattern.search(jsscript).group()
                pattern4PageNum = re.compile("\d+")
                maxPage = int(pattern4PageNum.search(maxPageString).group())

                # Find category path
                prod_CatePath = data.find(
                    class_="pathArea").ul.find_all('a')

                if data.find(class_="pageArea"):
                    currentPage = int(data.find(class_="pageArea").find(
                        class_="selected").a.getText())
                    if currentPage < maxPage and currentPage<=35:
                        print(f'Current page: {currentPage}/{maxPage}')
                        nextPageURL = f'https://m.momoshop.com.tw/cateGoods.momo?cn={prod_CatePath[-1]["cn"]}&page={str(currentPage+1)}&sourcePageType=4'
                        result = self.get_products(nextPageURL)
                        print(result)
                        
                        Products = Products+result['content']
                        if self.isExceedMessageSize(Products):
                            print("Exceed msg size limitation")
                            print(f' Send to SQS: {Products}')
                            self.send2SQS(Products)
                            Products=[]
                            # Record Product category path
                            Products.append({'Category': {}})
                            for element in prod_CatePath:
                                Products[-1]['Category'].update({f'L{element["catelevel"]}CateCode': element["cn"],
                                                                 f'L{element["catelevel"]}Category': element.getText()})
                    else:
                        print(f'Final page: {currentPage}/{maxPage}')
                        # Record Product category path
                        Products.append({'Category': {}})
                        for element in prod_CatePath:
                            Products[-1]['Category'].update({f'L{element["catelevel"]}CateCode': element["cn"],
                                                             f'L{element["catelevel"]}Category': element.getText()})       
                else:
                    print(f'Only one page: {maxPage}')
                    # Record Product category path
                    Products.append({'Category': {}})
                    for element in prod_CatePath:
                        Products[-1]['Category'].update({f'L{element["catelevel"]}CateCode': element["cn"],
                                                         f'L{element["catelevel"]}Category': element.getText()})
                    # print(f' Send to SQS: {Products}')
                    # self.send2SQS(Products)
                    # Products=[]
            return {'isProd': True, 'content': Products}
        else:
            print(
                f'\n----------\nURL:{url}\n Request return no data!\n----------\n')
            return {'isProd': False, 'content': {}}

    def send2SQS(self,data):
        randNum=int(1000*random.random()%1000)
        client = boto3.client('sqs')
        message = client.send_message(
            QueueUrl=os.environ['sqsUrl'],
            MessageBody=(
                json.dumps(data)
            ),
            MessageGroupId='momo-category',
            MessageDeduplicationId='momo-category' +str(randNum)
        )

    def isExceedMessageSize(self,Products):
        if len(json.dumps(Products).encode('utf-8')) > 200:
            return True
        else:
            return False

    def get_sale_counts(self, i_codes):

        url = f'https://eccapi.momoshop.com.tw/user/getGoodsSaleCounts'
        payload = {"host": "mobile", "goodsCode":i_codes}
        payload_json = json.dumps(payload)
        data = self.request_post(url, payload=payload_json)
        data=json.loads(data)

        if data["success"]:
            return data["saleCount"]
        else:
            print("Error!!!")

        return data
