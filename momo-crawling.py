import time
import json
import random
import requests
from urllib import parse
from bs4 import BeautifulSoup
import os
import re


class MomoSpider():
    """PChome線上購物 爬蟲"""

    def __init__(self):
        self.post_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://m.momoshop.com.tw',
            'Referer': 'https://m.momoshop.com.tw/',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode':'cors',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
        }
        self.get_headers1={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        self.get_headers2={
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
            r.encoding='UTF-8'
            data=BeautifulSoup(r.text, 'html.parser')
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
        # surl = 'https://www.momoshop.com.tw/main/Main.jsp?cid=memb&oid=back2hp&mdiv=1099800000-bt_0_150_01-bt_0_150_01_e1&ctype=B'


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


    def get_search_category(self, url):
        """取得搜尋商品分類

        :param keyword: 搜尋關鍵字
        :return data: 分類資料
        """
        # 起始網址為母嬰玩具頁面
        # url = f'https://m.momoshop.com.tw/category.momo?cn=2700000000&cid=dir&oid=dir&sourcePageType=4&imgSH=fourCardType'
        print(f'\nVisit url:{url}')
        data = self.request_get(url)

        if data:
            print("data is get successfully!")
            
            if data.find(class_="classificationArea jsCategoryList"):
                subCategories = []
                categoryList_html = data.find(
                class_="classificationArea jsCategoryList").dl.find_all('a')
                for element in categoryList_html:
                    item_title = element['title']
                    item_subActionValue = element['subactionvalue']
                    item_subActionType = element['subactiontype']
                    item_subCateCode = element['subcatecode']
                    item_subCateLevel = element['subcatelevel']
                    item = {
                        'Name': item_title,
                        'Level': item_subCateLevel,
                        'Code': item_subCateCode,
                        'ActionType': item_subActionType,
                        'ActionValue': item_subActionValue,
                        'Sub':[]
                    }
                    subCategories.append(item)

                HateList=["濕紙巾","玩具","積木","模型/公仔","桌遊","兒童成長傢俱","寢具/睡袋",
                        "書包/童包","文具用品","TOP30","館長推薦","活動專區","品牌總攬(A~Z)",
                        "主打活動","品牌推薦","披風","披巾" ,"背帶口水墊","揹巾保護墊","品牌總覽(A~Z)",
                        "授乳用品","便器/便盆/馬桶","精選大牌","沐浴網架/床","床配件","品牌強打","新生兒禮盒",
                        "枕類","被毯類","孕產期用品","品牌總覽","安全防護用品","戲水褲","尿片尿墊",
                          "本月主打活動", "快閃折扣", "限時出清", "特規超值組", "週期訂購", "登機車", "傘車", 
                          "置物袋", "枕", "輔助墊", "提籃蓋巾", "洗澡用品", "清潔劑", "哺乳巾", "奶瓶吸管配件",
                          "奶瓶刷", "奶粉盒", "收納盒", "鍊夾", "輔助器", "肚圍", "涼感巾", "睡箱/抱袋", "吸管刷",
                          "靠墊", "沙發墊", "睡袍", "零食杯碗", "其他配件", "水瓶", "水壺", "包巾/紗布巾", "防踢背心",
                          "包巾/抱袋", "安撫躺/搖椅", "床墊", "清潔/配件", "畫畫衣圍裙", "推車座墊"]

                categoryTobeDel=[]

                for i in range(len(subCategories)):
                    print(f'{subCategories[i]["Name"]}')
                    if not any(item in subCategories[i]["Name"] for item in HateList):
                        print("Not in HateList")
                        subURL = f'https://m.momoshop.com.tw/cateGoods.momo?cn={subCategories[i]["Code"]}&sourcePageType=4'
                        print(
                            f'Visit subCategory: {subCategories[i]["Name"]}{subCategories[i]["Code"]}')
                        result = self.get_search_category(subURL)
                        print(f'result["isProd"]: {result["isProd"]}')
                        if not result['isProd']:
                            subCategories[i]['Sub']=result['content']
                        time.sleep(0.2)
                    else:
                        print("In HateList, remove it")
                        categoryTobeDel.append(i)
                
                for item in sorted(categoryTobeDel,reverse=True):
                    if item < len(subCategories):
                        del subCategories[item]
                        
                if subCategories[0]['Level'] =='1':
                    cate_directory="momo-categories"
                    cate_path=self.make_dir(cate_directory)
                    cate_filename='momo-categories'
                    self.saveData(cate_path,cate_filename,subCategories)
                    print(f'Save category file:{cate_filename}.txt')
                return {'isProd':False, 'content':subCategories}
            else:
                print("Reach bottom category!")
                return {'isProd': True, 'content': {}}

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

    def get_products(self, url):
        data = self.request_get(url)
        if data:
            if data.find(class_="classificationArea jsCategoryList"):
                print(f'\n----------\nURL:{url}\n Not a bottom category!\n----------\n')
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
                        'Price': int(Prd_Price.replace(',','')),
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
                    if currentPage < maxPage:
                        print(f'Current page: {currentPage}/{maxPage}')
                        nextPageURL = f'https://m.momoshop.com.tw/cateGoods.momo?cn={prod_CatePath[-1]["cn"]}&page={str(currentPage+1)}&sourcePageType=4'
                        result = self.get_products(nextPageURL)
                        Products = Products+result['content']
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
            return {'isProd': True, 'content': Products}
        else:
            print(f'\n----------\nURL:{url}\n Request return no data!\n----------\n')
            return {'isProd': False, 'content': {}}

    def to_bottomCategory(self, List):
        for item in List:
            if item["Sub"]:
                self.to_bottomCategory(item["Sub"])
            else:
                url = f"https://m.momoshop.com.tw/cateGoods.momo?cn={item['Code']}&sourcePageType=4"
                result=self.get_products(url)
                
                prod_directory = "momo-prod"
                prod_path = self.make_dir(prod_directory)
                prod_filename = f'momo-prod-{item["Code"]}'
                self.saveData(prod_path, prod_filename, result['content'])
                print(f'Save category file:{prod_filename}.txt')


                



    # def testimony(self):
     
        # url = f'https://eccapi.momoshop.com.tw/user/getGoodsComment'
        # url=f'https://eccapi.momoshop.com.tw/user/getGoodsSaleCounts'
        # payload = {"host": "mobile", "goodsCode":
        #            ["10601195", "10586280"]}
        # payload_json=json.dumps(payload)
        # # FormData=parse.urlencode(payload)
        # data = self.request_post(url,payload=payload_json, headers=self.post_headers, to_json=False)

        # return data
        return None


if __name__ == '__main__':
    momo_spider = MomoSpider()
    
    # 起始網址為母嬰玩具頁面
    url = f'https://m.momoshop.com.tw/category.momo?cn=2700000000&cid=dir&oid=dir&sourcePageType=4&imgSH=fourCardType'
    result=momo_spider.get_search_category(url)

    wishlist = ["奶瓶", "奶嘴", "消毒鍋", "溫奶器", "嬰兒床", "澡盆", "尿布", "紙尿褲", "汽座", "推車",
                "餐盤", "餐碗", "餐椅", "副食品", "口水", "圍兜", "固齒器", "水杯", "遊戲地墊", "地墊", "圍欄", "牙刷"]

    with open(os.path.join(os.getcwd(),'momo-categories/momo-categories.txt')) as f:
        Categories = json.load(f)

    for subL1 in Categories:
        Prod=momo_spider.to_bottomCategory(subL1["Sub"])





