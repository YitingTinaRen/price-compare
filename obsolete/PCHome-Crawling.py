import time
import json
import random
import requests
import pandas as pd
from pandas import json_normalize
import os
import math


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

    def search_products(self, keyword, max_page=1, shop='全部', sort='有貨優先', price_min=-1, price_max=-1, is_store_pickup=False, is_ipost_pickup=False):
        """搜尋商品

        :param keyword: 搜尋關鍵字
        :param max_page: 抓取最大頁數
        :param shop: 賣場類別 (全部、24h購物、24h書店、廠商出貨、PChome旅遊)
        :param sort: 商品排序 (有貨優先、精準度、價錢由高至低、價錢由低至高、新上市)
        :param price_min: 篩選"最低價" (需與 price_max 同時用)
        :param price_max: 篩選"最高價" (需與 price_min 同時用)
        :param is_store_pickup: 篩選"超商取貨"
        :param is_ipost_pickup: 篩選"i 郵箱取貨"
        :return products: 搜尋結果商品
        """
        products = []
        all_shop = {
            '全部': 'all',
            '24h購物': '24h',
            '24h書店': '24b',
            '廠商出貨': 'vdr',
            'PChome旅遊': 'tour',
        }
        all_sort = {
            '有貨優先': 'sale/dc',
            '精準度': 'rnk/dc',
            '價錢由高至低': 'prc/dc',
            '價錢由低至高': 'prc/ac',
            '新上市': 'new/dc',
        }

        url = f'https://ecshweb.pchome.com.tw/search/v3.3/{all_shop[shop]}/results'
        params = {
            'q': keyword,
            'sort': all_sort[sort],
            'page': 0
        }
        if price_min >= 0 and price_max >= 0:
            params['price'] = f'{price_min}-{price_max}'
        if is_store_pickup:
            params['cvs'] = 'all'   # 超商取貨
        if is_ipost_pickup:
            params['ipost'] = 'Y'   # i 郵箱取貨

        while params['page'] < max_page:
            params['page'] += 1
            data = self.request_get(url, params)
            if not data:
                print(f'請求發生錯誤：{url}{params}')
                break
            if data['totalRows'] <= 0:
                print('找不到有關的產品')
                break
            products.extend(data['prods'])
            if data['totalPage'] <= params['page']:
                break
        return products

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
        
        with open('pchome-L1categories.txt', 'w', encoding='utf-8') as f:
            json.dump(data,f,ensure_ascii=False, indent=4)
        # df = json_normalize(data)
        # df.to_csv("pchome-L1Categories.csv")

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

    def testimony(self):
        # url = f'https://ecapi-cdn.pchome.com.tw/cdn/ecshop/prodapi/v2/store/DEAU5X/prod&offset=8&limit=36&fields=Id,Nick,Pic,Price,Discount,isSpec,Name,isCarrier,isSnapUp,isBigCart,OriginPrice,iskdn,isPreOrder24h,PreOrdDate,isWarranty,isFresh,isBidding,isETicket,ShipType,isO2O,isSubscription,ButtonType&_callback=jsonp_prodgrid?_callback=jsonp_prodgrid'
        # url= f'https://ecapi-cdn.pchome.com.tw/cdn/ecshop/prodapi/v2/store/DECHCO/prod&offset=5&limit=36&fields=Id,Nick,Pic,Price,Discount,Name,OriginPrice&_callback=jsonp_prodgrid'
        # url = f'https://ecapi-cdn.pchome.com.tw/ecshop/prodapi/v2/prod/button&id=DEAIC5-A900FMES1,DEAIC5-A900C33GZ,DEAIC5-A900FGQ1X,DEAIC5-A900BOJMH&fields=Id,Qty,ButtonType,Price,isPrimeOnly,Device&_callback=jsonp_prodtop_button'
        # url = f'https://ecapi-cdn.pchome.com.tw/cdn/ecshop/prodapi/v2/prod/DECHAV-A900FLB9R/desc&fields=Id,Stmt,Equip,Remark,Liability,Kword,Slogan,Author,Transman,Pubunit,Pubdate,Approve,Meta&_callback=jsonp_desc'
        url = f'https://ecapi-cdn.pchome.com.tw/cdn/ecshop/prodapi/v2/store/DECHCQ/prod&offset=5&limit=36&fields=Id,Nick,Pic,Price,Discount,isSpec,Name,isCarrier,isSnapUp,isBigCart,OriginPrice,iskdn,isPreOrder24h,PreOrdDate,isWarranty,isFresh,isBidding,isETicket,ShipType,isO2O,isSubscription&_callback=jsonp_prodgrid'
        data = self.request_get(url)


        
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




if __name__ == '__main__':
    pchome_spider = PchomeSpider()
    # Categories=pchome_spider.get_categories_L2()

    
    with open('pchome-L1Categories.txt') as f:
        Categories=json.load(f)
    
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
                    dir_path = pchome_spider.make_dir(folder)
                    filename = L2Categories['Id']+'_prod'
                    pchome_spider.saveData(dir_path, filename, Products)

                    # Get salestatus of products
                    ProdSaleStatus = pchome_spider.get_products_sale_status(ProIdList)
                    SaleStatusFolder='pchome-salestatus'
                    path=pchome_spider.make_dir(SaleStatusFolder)
                    filename = L2Categories['Id']+'_salestatus'
                    pchome_spider.saveData(path, filename, ProdSaleStatus)

                    # # Get specification of products
                    # ProdSpec = pchome_spider.get_products_specification(ProIdList)
                    # SpecFolder='pchome-spec'
                    # path=pchome_spider.make_dir(SpecFolder)
                    # filename = L2Categories['Id']+'_spec'
                    # pchome_spider.saveData(path,filename,ProdSpec)

                    # Get descriptions of products
                    ProdDesc = pchome_spider.get_products_description(ProIdList)
                    SpecFolder = 'pchome-desc'
                    path = pchome_spider.make_dir(SpecFolder)
                    filename = L2Categories['Id']+'_desc'
                    pchome_spider.saveData(path, filename, ProdDesc)

                    visitedlist.append(L2Categories['Id'])
                    time.sleep(0.2)

    

        

