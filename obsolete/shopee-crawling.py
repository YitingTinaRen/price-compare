import time
import json
import random
import requests


class ShopeeSpider():
    """PChome線上購物 爬蟲"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'referer': 'https://shopee.tw/%E5%A4%96%E5%87%BA%E7%94%A8%E5%93%81-cat.11040542.11042186?facet=100946&filters=5&page=0&sortBy=pop',
            'x-api-source': 'pc',
        }
        self.session_headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'referer':'https://shopee.tw/',
            'x-api-source':'pc',
        }

    def request_get(self, url, params=None, to_json=True):
        """送出 GET 請求

        :param url: 請求網址
        :param params: 傳遞參數資料
        :param to_json: 是否要轉為 JSON 格式
        :return data: requests 回應資料
        """
        s=requests.Session()
        surl = 'https://shopee.tw/api/v4/deep_platform/ab_test/get_all_variates?project_numbers=0'
        r=s.get(surl, headers=self.session_headers)
        print(r.headers)
        r=s.get(url, headers=self.headers)
        print(r.url)
        if r.status_code != requests.codes.ok:
            print(f'網頁載入發生問題：{url}')
        try:
            if to_json:
                data = r.json()
            else:
                data = r.text
        except Exception as e:
            print(e)
            return None
        return data

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

        :param products_id: 商品 ID
        :return data: 商品販售狀態資料
        """
        if type(products_id) == list:
            products_id = ','.join(products_id)
        url = f'https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id={products_id}'
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
        data = self.request_get(url, to_json=False)
        # 去除前後 JS 語法字串
        data = json.loads(data[17:-48])
        return data

    def get_search_category(self, keyword):
        """取得搜尋商品分類(網頁左側)

        :param keyword: 搜尋關鍵字
        :return data: 分類資料
        """
        url = f'https://ecshweb.pchome.com.tw/search/v3.3/all/categories?q={keyword}'
        data = self.request_get(url)
        return data

    def get_search_categories_name(self, categories_id):
        """取得商品子分類的名稱(網頁左側)

        :param categories_id: 分類 ID
        :return data: 子分類名稱資料
        """
        if type(categories_id) == list:
            categories_id = ','.join(categories_id)
        url = f'https://ecapi-pchome.cdn.hinet.net/cdn/ecshop/cateapi/v1.5/store&id={categories_id}&fields=Id,Name'
        data = self.request_get(url)
        return data

    def testimony(self):
        # url = f'https://ecapi-cdn.pchome.com.tw/cdn/ecshop/cateapi/v1.6/region/DEAU/menu&_callback=jsonp_nemu&5581634?_callback=jsonp_nemu'
        url = f'https://shopee.tw/api/v4/search/search_items?by=pop&categoryids=100946&fe_categoryids=11042186&filters=5&limit=60&newest=0&order=desc&page_type=search&scenario=PAGE_CATEGORY&version=2'
        data = self.request_get(url,to_json=False)


        
        return data

    def remove_js(self,str):
        str_len=len(str)
        # str_1 = str.replace("try{jsonp_nemu(", "")
        str_1 = str.replace("try{jsonp_prodgrid(", "")
        str_replaced = str_1.replace(
            ");}catch(e){if(window.console){console.log(e);}}", "")
        return str_replaced


if __name__ == '__main__':
    shopee_spider = ShopeeSpider()
    result = shopee_spider.testimony()
    # for item in result:
    #     # print("Name: {name}, Id: {ID}".format(name=item['Name'], ID=item['Id']) )
    #     print("Name: {name}, Id: {ID}, Price: {price}".format(
    #         name=item['Name'], ID=item['Id'], price=item['Price']['P']))
    print(result)

