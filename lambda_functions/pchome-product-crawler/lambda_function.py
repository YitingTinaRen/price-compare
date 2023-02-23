import json
import boto3
import random
import requests
import os
import time
import math

def lambda_handler(event, context):
    # TODO implement
    print(event['Records'][0]['body'])
    print(type(event['Records'][0]['body']))
    L2Categories = json.loads(event['Records'][0]['body'])
    print(L2Categories)
    print(type(L2Categories))


    pchome_spider = PchomeSpider()
    Total_prod_num = pchome_spider.get_products_count(
        L2Categories['Id'])
    maxPage = math.ceil(Total_prod_num/36)

    # Collect products information here
    Products = []
    ProdSale=[]
    ProdDescrip=[]
    for page in range(maxPage):
        if page == 0:
            Prod=pchome_spider.get_products(L2Categories['Id'], 0)
        else:
            Prod = pchome_spider.get_products(
                L2Categories['Id'], 36*page+1)
        
        # Organize product id lists for calling sale status and product description function
        ProIdList = [sub['Id'] for sub in Prod]
        ProIdList = [sub.replace('-000', '') for sub in ProIdList]
        
        ProdSaleStatus = pchome_spider.get_products_sale_status(ProIdList)
        ProdSale=ProdSale+ProdSaleStatus

        ProdDesc = pchome_spider.get_products_description(ProIdList)
        ProdDescrip.append(ProdDesc)
        Products=Products+Prod
        if isExceedMessageSize(Products, ProdSale,ProdDescrip,L2Categories):
            Send2SQS(Products, ProdSale, ProdDescrip, L2Categories)
            Products=[]
            ProdSale=[]
            ProdDescrip=[]
        time.sleep(0.3)
    
    if Products:
        Send2SQS(Products, ProdSale, ProdDescrip, L2Categories)
    
    # # Organize product id lists for calling sale status and product description function
    # ProIdList = [sub['Id'] for sub in Products]
    # ProIdList = [sub.replace('-000', '') for sub in ProIdList]
    
    # # append categories into the product list data
    # Products.append(L2Categories['Category'])
    
    # # Get salestatus of products
    # ProdSaleStatus = pchome_spider.get_products_sale_status(ProIdList)
    # Products.append({"salestatus":ProdSaleStatus})

    # # Get descriptions of products
    # ProdDesc = pchome_spider.get_products_description(ProIdList)
    # Products.append({"description":ProdDesc})

    # client = boto3.client('sqs')
    # message= client.send_message(
    #     QueueUrl=os.environ['sqsUrl'],
    #     MessageBody=(
    #         json.dumps(Products)
    #     ),
    #     MessageGroupId='pchome-prod',
    #     MessageDeduplicationId='pchome-prod-'+L2Categories['Id']
    # )

    time.sleep(0.2)


    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def Send2SQS(Products, ProdSale, ProdDescrip, L2Categories):
    Products.append(L2Categories['Category'])
    Products.append({"salestatus": ProdSale})
    Products.append({"description": ProdDescrip})

    client = boto3.client('sqs')
    message = client.send_message(
        QueueUrl=os.environ['sqsUrl'],
        MessageBody=(
            json.dumps(Products)
        ),
        MessageGroupId='pchome-prod',
        MessageDeduplicationId='pchome-prod-'+L2Categories['Id']
    )

def isExceedMessageSize(Products, ProdSale, ProdDescrip, L2Categories):
    Products.append(L2Categories['Category'])
    Products.append({"salestatus": ProdSale})
    Products.append({"description": ProdDescrip})
    if len(json.dumps(Products).encode('utf-8'))>200:
        return True
    else:
        return False


class PchomeSpider():
    """PChome線上購物 爬蟲"""

    def __init__(self):
        self.headers1 = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }
        self.headers2 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }
        self.headers3 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
        }

    def request_get(self, url, params=None):
        """送出 GET 請求

        :param url: 請求網址
        :param params: 傳遞參數資料
        :param to_json: 是否要轉為 JSON 格式
        :return data: requests 回應資料
        """
        #用亂數去切換每次request的user agent來增加爬蟲成功率
        list4rand=[1,2,3]
        randNum= random.choice(list4rand)
        if randNum == 1:
            r = requests.get(url, params, headers=self.headers1)
        elif randNum ==2:
            r = requests.get(url, params, headers=self.headers2)
        else:
            r = requests.get(url, params, headers=self.headers3)

        if r.status_code != requests.codes.ok:
            print(f'[Request error]網頁載入發生問題：{url}')
        try:
            data = r.text
            data=self.remove_js(data,url)
            data=json.loads(data)
        except Exception as e:
            print(e)
            return None
        return data

    def remove_js(self, str, url):
        str_1 = str.replace("try{jsonp_"+url[url.find("jsonp_")+6:]+"(", "")
        str_replaced = str_1.replace(
            ");}catch(e){if(window.console){console.log(e);}}", "")

        return str_replaced


    def get_products_sale_status(self, products_id):
        """取得商品販售狀態

        :param products_id: 商品 ID, 需整理成list
        :return data: 商品販售狀態資料
            ex:
            "Seq": 25076544,
            "Id": "DAAT0S-A900ARGK7-000",
            "Store": "DAAT0S",
            "Price": {
                "M": 89,
                "P": 89,
                "Prime": "",
                "Low": null
            },
            "Qty": 20,
            "ButtonType": "ForSale",
            "SaleStatus": 1,
            "Group": "DAAT0S-A900ARGK7",
            "isPrimeOnly": 0,
            "SpecialQty": 0,
            "Device": []
        """
        if type(products_id) == list:
            products_id = ','.join(products_id)
        url = f'https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id={products_id}&fields=Id,ButtonType&_callback=jsonp_prodtop_button'
        data = self.request_get(url)
        if not data:
            print(f'請求發生錯誤：{url}')
            return []
        return data

    def get_products_specification(self, products_id):
        """取得商品規格種類

        :param products_id: 商品 ID
        :return data: 商品規格種類
        """
        if type(products_id) == list:
            products_id = ','.join(products_id)
        url = f'https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/spec&id={products_id}&_callback=jsonpcb_spec'
        data = self.request_get(url)
        return data

    def get_products_description(self, products_id):
        if type(products_id) == list:
            products_id = ','.join(products_id)
        url = f'https://ecapi-cdn.pchome.com.tw/cdn/ecshop/prodapi/v2/prod/desc&id={products_id}&fields=Id,Slogan&_callback=jsonp_prodtop_slogan'
        data = self.request_get(url)
        return data


    def get_products(self, categoryID, offsetNum):
        """取得分類底下產品列表
            可取得資訊: 
            ProductID
            ProductNickname
            ProductName
            Price(Price-P)
            Discount
            Pic: PicB is the main picture
            OriginalPrice(Price-M)

            offsetNum:索取資料的起始值
        """
        url = f'https://ecapi-cdn.pchome.com.tw/cdn/ecshop/prodapi/v2/store/{categoryID}/prod&offset={offsetNum}&limit=36&fields=Id,Nick,Pic,Price,Discount,Name,OriginPrice&_callback=jsonp_prodgrid'
        data = self.request_get(url)
        
        if not data:
            print(f'請求發生錯誤：{url}')
            return []
        return data

    def get_products_count(self, categoryID):
        """取得分類底下一共有多少個產品"""
        url = f'https://ecapi-cdn.pchome.com.tw/cdn/ecshop/prodapi/v2/store/{categoryID}/prod/count&_callback=jsonp_prodcount'
        data=self.request_get(url)

        return data