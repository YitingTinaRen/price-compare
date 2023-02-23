import time
import json
import random
import requests
import os
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # TODO implement
    pchome_spider = PchomeSpider()
    Categories=pchome_spider.get_categories_L2()
    
    wishlist=["奶瓶","奶嘴","消毒","溫奶器","嬰兒床","澡盆","尿布","紙尿褲","汽座",
                "推車","餐盤","餐碗","兒童餐椅","副食品","口水","圍兜","固齒器","水杯",
                "遊戲地墊", "地墊", "圍欄", "牙刷", "安全座椅", "NB(約5kg以下)",
                "黏貼型M(約6-11kg)", "褲型M(約6-11kg)", "6個月", "褲型L(約9-14kg)", 
                "黏貼型L(約9-14kg)", "褲型XL(約12kg以上)"]
    L0Category={"DECH": "嬰童", "DEAI": "婦幼", "DEAU": "推車汽座", "DAAO": "尿布"}
    hatelist=["活動專區","折價券","滿額","狂銷","每日","玩水褲", "期間","哈燒話題",
                "特價","教具","書包","免運","本月","童裝","內著","織品","包屁衣","連身裝","上衣",
                "襯衫", "背心", "外套", "褲/裙/吊帶/洋裝", "眼鏡", "玩具", "三輪車",
                "手推車配件", "品牌總覽", "汽座配件", "兒童雨具雨衣", "防蚊／除臭／除菌", "防蚊／除臭／除菌",
                "媽媽包", "親子包", "泳具", "親子野餐日", "護理保健", "抗菌", "防蚊", "清潔用品", "沐浴保養潔牙", "濕巾護理巾"]
    
    visitedlist=[]
    
    for L0CategoryId in Categories:
        print('Category ID: {}'.format(L0CategoryId))
        
        for L1Categories in Categories[L0CategoryId]:
            print('Level 1 category ID: {}, Name:{}'.format(
                L1Categories['Id'], L1Categories['Name']))
            if L0CategoryId == "DAAO" and L1Categories["Id"] != "DAAO16C":
                print("Skip!")
                continue
            if L0CategoryId == "DEAI" and (L1Categories["Id"] in ["DEAI63C", "DEAI57C", "DEAI19C", "DEAI70C", "DEAI16C", "DEAI06C", "DEAI02C", "DEAI35C", "DEAI33C", "DEAI10C", "DEAI93C", "DEAI01C", "DEAI51C", "DEAI61C", "DEAI58C", "DEAI91C", "DEAI85C", "DEAI79C", "DEAI75C", "DEAI83C", "DEAI27C", "DEAI97C", "DEAI59C", "DEAI99C", "DEAI98C", "DEAI96C", "DEAI52C"]):
                print("Skip!")
                continue
            if any(item in L1Categories["Name"] for item in hatelist):
                print("In hate list!")
                continue
            
            for L2Categories in L1Categories['Nodes']:
                if any(L2Categories['Id'] in item for item in visitedlist):
                    continue
                print('Level 2 ID: {}, Name:{}'.format(
                    L2Categories['Id'], L2Categories['Name']))

                if any(item in L2Categories['Name'] for item in wishlist):
                    print("Category in wishlist, save to sqs")
                    
                    client = boto3.client('sqs')
                    message= client.send_message(
                        QueueUrl=os.environ['sqsUrl'],
                        MessageBody=(
                            json.dumps(
                                {
                                    "Id":L2Categories['Id'],
                                    'Category':{
                                        'L0CategoryCode': L0CategoryId, 'L0CategoryName': L0Category[L0CategoryId],
                                        'L1CategoryCode': L1Categories['Id'], 'L1CategoryName': L1Categories['Name'],
                                        'L2CategoryCode': L2Categories['Id'], 'L2CategoryName': L2Categories['Name']
                                    }
                                }
                            )
                        ),
                        MessageGroupId='pchome-category',
                        MessageDeduplicationId='pchome-category'+L2Categories['Id']
                    )

    return {
        'statusCode': 200,
        'body': json.dumps('pchome category crawling is successfull!')
    }

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


    def get_categories_L2(self):
        """取得商品子分類的名稱(網頁左側)

        :param categories_id: 分類 ID
        L0 category IDs:
            DECH:嬰童
            DEAI:婦幼
            DEAU:推車汽座
            DAAT:濕紙巾
            DAAO:尿布
        :return data: 子分類名稱資料
        """
        L1_category_ids = ['DAAT', 'DECH', 'DAAO', 'DEAI', 'DEAU']
        data={"DAAT":None, "DECH":None, "DAAO":None, "DEAI":None, "DEAU":None}
        for item in L1_category_ids:
            url = f'https://ecapi-cdn.pchome.com.tw/cdn/ecshop/cateapi/v1.6/region/{item}/menu&_callback=jsonp_menu'
            data[item] = self.request_get(url)

            if not data[item]:
                print(f'請求發生錯誤：{url}')
            
            time.sleep(1)

        return data



