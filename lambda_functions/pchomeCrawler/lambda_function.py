import time
import json
import random
import requests
import os
import math
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # TODO implement
    pchome_spider = PchomeSpider()
    Categories=pchome_spider.get_categories_L2()
    
    wishlist=["奶瓶","奶嘴","消毒","溫奶器","嬰兒床","澡盆","尿布","紙尿褲","汽座",
                "推車","餐盤","餐碗","餐椅","副食品","口水","圍兜","固齒器","水杯",
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
                    print("Category in wishlist, collecting data")
                    # Get total product number
                    Total_prod_num = pchome_spider.get_products_count(
                        L2Categories['Id'])
                    maxPage = math.ceil(Total_prod_num/36)

                    # Collect products information here
                    Products = []
                    for page in range(maxPage):
                        if page == 0:
                            Prod=pchome_spider.get_products(L2Categories['Id'], 0)
                        else:
                            Prod = pchome_spider.get_products(
                                L2Categories['Id'], 36*page+1)
                        
                        Products=Products+Prod
                        time.sleep(0.5)
                    
                    # Organize product id lists for calling sale status and product description function
                    ProIdList = [sub['Id'] for sub in Products]
                    ProIdList = [sub.replace('-000', '') for sub in ProIdList]
                    
                    # append categories into the product list data
                    Products.append(
                        {'Category': {'L0CategoryCode': L0CategoryId, 'L0CategoryName': L0Category[L0CategoryId],
                        'L1CategoryCode': L1Categories['Id'], 'L1CategoryName': L1Categories['Name'],
                        'L2CategoryCode': L2Categories['Id'], 'L2CategoryName': L2Categories['Name']}})
                    
                    # Save products data
                    folder = 'pchome-prod'
                    # dir_path = pchome_spider.make_dir(folder)
                    filename = L2Categories['Id']+'_prod'
                    pchome_spider.upload_file(Products,filename, folder)

                    # Get salestatus of products
                    ProdSaleStatus = pchome_spider.get_products_sale_status(ProIdList)
                    SaleStatusFolder='pchome-salestatus'
                    # path=pchome_spider.make_dir(SaleStatusFolder)
                    filename = L2Categories['Id']+'_salestatus'
                    pchome_spider.upload_file(ProdSaleStatus,filename,SaleStatusFolder)

                    # # Get specification of products
                    # ProdSpec = pchome_spider.get_products_specification(ProIdList)
                    # SpecFolder='pchome-spec'
                    # path=pchome_spider.make_dir(SpecFolder)
                    # filename = L2Categories['Id']+'_spec'
                    # pchome_spider.saveData(path,filename,ProdSpec)

                    # Get descriptions of products
                    ProdDesc = pchome_spider.get_products_description(ProIdList)
                    DescFolder = 'pchome-desc'
                    # path = pchome_spider.make_dir(DescFolder)
                    filename = L2Categories['Id']+'_desc'
                    pchome_spider.upload_file(ProdDesc,filename,DescFolder)

                    visitedlist.append(L2Categories['Id'])
                    time.sleep(0.2)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
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

    def upload_file(self,file, object_name, folder_name):
        """Upload a file to an S3 bucket

        :param file: File to upload
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            print("No object_name")
            return False

        # Upload the file
        s3_client = boto3.client('s3',
                    aws_access_key_id=os.environ['S3_KEY_ID'],
                    aws_secret_access_key=os.environ['S3_SECRET_KEY'])
        try:
            # response = s3_client.upload_file(file_name, config.S3_BUCKET, object_name)
            response=s3_client.put_object(
                Bucket=os.environ['S3_BUCKET'],
                Body= json.dumps(file),
                Key=folder_name+"/"+object_name
            )
        except ClientError as e:
            print(e)
            return False
        return True

    def read_file(self,object_name):
        s3_client =boto3.client('s3')
        s3_bucket_name=os.environ['S3_BUCKET']
        data=s3_client.get_object(Bucket=s3_bucket_name, Key=object_name)
        return data

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
        url = f'https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id={products_id}&_callback=jsonp_prodtop_button'
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

    def get_search_category(self, keyword):
        """取得搜尋商品分類(網頁左側)

        :param keyword: 搜尋關鍵字
        :return data: 分類資料
        """
        url = f'https://ecshweb.pchome.com.tw/search/v3.3/all/categories?q={keyword}'
        data = self.request_get(url)
        return data

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
        
        # with open('pchome-L1categories.txt', 'w', encoding='utf-8') as f:
        #     json.dump(data,f,ensure_ascii=False, indent=4)
        
        self.upload_file(data, 'pchome-categories','pchome-categories')

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


    def make_dir(self,directory):
        # get current path
        currentPath = os.getcwd()
        path = os.path.join(currentPath,directory)
        if not os.path.exists(path):
            os.mkdir(path)
            print('Folder is newly created')
        else:
            print('Folder already exists!')
        
        return path

    def saveData(self,path, filename, data):
        """Save data as txt file in JSON format
            return true if file is saved successfully
            else return false
        """
        try:
            with open(path+'/'+filename+'.txt', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(e)
            return False


