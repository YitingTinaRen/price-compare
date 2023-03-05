import mysql.connector
import config
from mysql.connector import errorcode
from operator import add

# MySQL Database config
dbconfig = {
	"host": config.DB_HOST,
	"user": config.DB_USER,
	"password": config.DB_PASSWORD,
	"database": config.DB_DB
}


# Create MySQL pooling
mydb = mysql.connector.connect(
	pool_name=config.DB_POOL_NAME,
	pool_size=config.DB_POOL_SIZE,
	**dbconfig
)
mydb.close()


class db:
    def checkAllData(sql, val=()):
        # return data type is dictionary
        mydb = mysql.connector.connect(pool_name=config.DB_POOL_NAME)
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()  # fetch all data
        mycursor.close()
        mydb.close()
        return myresult

    def checkOneData(sql, val=()):
        # return data type is dictionary
        mydb = mysql.connector.connect(pool_name=config.DB_POOL_NAME)
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchone()  # fetch one data
        mycursor.close()
        mydb.close()
        return myresult

    def writeData(sql, val):
        try:
            mydb = mysql.connector.connect(pool_name=config.DB_POOL_NAME)
            mycursor = mydb.cursor()
            mycursor.execute(sql, val)
            mydb.commit()
            mycursor.close()
            mydb.close()
            return True
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            return False
    
    def ProductMatchV2(ProdName, English, Chinese):
        print("in ProductMatchV2 function")

        ProdName = ProdName.replace("+", " ")
        ProdName = ProdName.replace("/", " ")
        ProdName = ProdName.replace("-", " ")
        ProdName = ProdName.replace(")", " ")
        ProdName = ProdName.replace("(", " ")

        if ProdName.find('】') == -1:
            l = []
            if ProdName.find(' ') == -1:
                l.append(ProdName)
            else:
                l.append(ProdName[:ProdName.index(' ')])
                l.append(ProdName[ProdName.index(' ')+1:])

            ProdName = l
        else:
            ProdName = ProdName.split('】')
            ProdName[0] = ProdName[0].replace("【", "")

        sql = """
                select ProductID, ProductName,ProductNick, CurrentPrice, ProductURL, EnglishWords,ChineseWords,
                match(EnglishWords) against(%s in boolean mode) as rel1,
                match(ChineseWords) against(%s in boolean mode) as rel2
                from PCHomeProducts 
                where match(EnglishWords) against(%s in boolean mode)
                and match(ChineseWords) against(%s in boolean mode) >10
                and ProductID 
                in (select ProductID 
                    from PCHomeProducts 
                    where ProductName like %s
                        or ProductNick like %s
                    )
                ;
                """
        val = (English, Chinese, English, Chinese,
            '%'+ProdName[0]+'%', '%'+ProdName[0]+'%',)
        result = db.checkAllData(sql, val)
        if result:
            Eng_point = []
            Eng_matchRate=[]
            Chi_point = []
            Chi_matchRate=[]
            for i in range(len(result)):
                print(
                    f'PCHome Product name:{result[i]["ProductName"]}, English match score:{result[i]["rel1"]}, Chinese match score:{result[i]["rel2"]}')
                Eng_point.append(len(list(set(result[i]['EnglishWords'].lower().split(
                    ' ')).intersection(set(English.lower().split(' '))))))
                Eng_matchRate.append(len(list(set(result[i]['EnglishWords'].lower().split(
                    ' ')).intersection(set(English.lower().split(' ')))))/len(list(set(result[i]['EnglishWords'].lower().split(
                        ' ')).union(set(English.lower().split(' '))))))
                Chi_point.append(len(list(set(result[i]['ChineseWords'].split(
                    ' ')).intersection(set(Chinese.split(' '))))))
                Chi_matchRate.append( len(list(set(result[i]['ChineseWords'].split(
                    ' ')).intersection(set(Chinese.split(' ')))))/len(list(set(result[i]['ChineseWords'].split(
                        ' ')).union(set(Chinese.split(' '))))) )

            total_point = list(map(add, Eng_point, Chi_point))
            index = total_point.index(max(total_point))
            print(f'Max Eng_point: {Eng_point[index]}')
            print(f'Eng_matchRate at Max Eng_point: {Eng_matchRate[index]}')
            print(f'Max Chi_pint: {Chi_point[index]}')
            print(f'Chi_matchRate at max Chi_point: {Chi_matchRate[index]}')

            print(f'Total_point={total_point}')
            print(f'English rate={Eng_matchRate}')
            print(f'Chinese rate={Chi_matchRate}')

            if Chi_matchRate[index]<0.6:
                result=[]
            else:
                result = result[index]
        return result

    def SearchProductbyCategory(CateLevel,CateName, ProdName):
        sql = """
            select P.ProductID, P.ProductName, P.CurrentPrice, P.ProductURL,C.CategoryName, P.EnglishWords, P.ChineseWords 
            from MomoProdCategory as C 
            inner join MomoProducts as P 
            on C.ProductID=P.ProductID 
            where C.CategoryLevel=%s and C.CategoryName like %s and P.ProductName like %s 
            ;
            """
        val = (CateLevel, "%"+CateName+"%", "%"+ProdName+"%",)
        result = db.checkAllData(sql, val)
        return result
    
    def writeMatchResult(MomoProductID,PCHProductID, MyCate):
        sql="""
            update MomoProducts
            set PCHProductID=%s, HasMatching=TRUE, MyCategory=%s where ProductID = %s;
        """
        val=(PCHProductID, MyCate,MomoProductID,)
        result=db.writeData(sql,val)
        # print(f'Table update result: {result}')
        return result
    
    def writeNoMatchResult(MomoProductID):
        sql = """
            update MomoProducts
            set PCHProductID=NULL, HasMatching=FALSE, MyCategory=NULL where ProductID = %s;
        """
        val = (MomoProductID,)
        result = db.writeData(sql, val)
        return result


if __name__ == '__main__':
    match_condition = [
        # {'MyCate': '副食品分裝盒', 'CateName': '副食品',
        #     'ProdName': '副食品分裝盒', 'CateLevel': '3'},
        # {'MyCate': '固齒器', 'CateName': '固齒器',
        #     'ProdName': '固齒器', 'CateLevel': '3'},
        # {'MyCate': '水杯', 'CateName': '水杯',
        #     'ProdName': '水杯', 'CateLevel': '2'},
        {'MyCate': '消毒鍋', 'CateName': '消毒',
            'ProdName': '消毒', 'CateLevel': '3'},
        # {'MyCate': '圍欄', 'CateName': '圍欄',
        #  'ProdName': '圍欄', 'CateLevel': '3'},
        # {'MyCate': '澡盆', 'CateName': '澡盆',
        #  'ProdName': '澡盆', 'CateLevel': '3'},
        # {'MyCate': '汽座', 'CateName': '汽座',
        #  'ProdName': '汽座', 'CateLevel': '3'},
        # {'MyCate': '餐椅', 'CateName': '餐椅',
        #  'ProdName': '餐椅', 'CateLevel': '3'},
        # {'MyCate': '地墊', 'CateName': '地墊',
        #  'ProdName': '地墊', 'CateLevel': '3'},
        # {'MyCate': '奶瓶', 'CateName': '奶瓶',
        #  'ProdName': '奶瓶', 'CateLevel': '3'},
        # {'MyCate': '奶嘴', 'CateName': '奶嘴',
        #  'ProdName': '奶嘴', 'CateLevel': '3'},
        # {'MyCate': '溫奶器', 'CateName': '溫奶器',
        #  'ProdName': '溫奶器', 'CateLevel': '3'},
        # {'MyCate': '推車', 'CateName': '推車',
        #  'ProdName': '推車', 'CateLevel': '3'},
        # {'MyCate': '副食品調理器', 'CateName': '調理',
        #  'ProdName': '調理', 'CateLevel': '3'},
        # {'MyCate': '口水巾', 'CateName': '口水巾',
        #  'ProdName': '口水巾', 'CateLevel': '3'},
        # {'MyCate': '圍兜', 'CateName': '圍兜',
        #  'ProdName': '圍兜', 'CateLevel': '3'},
        # {'MyCate': '餐椅', 'CateName': '餐椅',
        #  'ProdName': '餐椅', 'CateLevel': '3'},
        # {'MyCate': '餐碗', 'CateName': '餐具',
        #  'ProdName': '餐碗', 'CateLevel': '3'},
        # {'MyCate': '餐盤', 'CateName': '餐具',
        #  'ProdName': '餐盤', 'CateLevel': '3'},
    ]
    
    for item in match_condition:
        result = db.SearchProductbyCategory(
            item['CateLevel'], item['CateName'], item['ProdName']) 


        
        for i in range(231,260):
        # for i in range(len(result)):
            print(f"\n\n{i}/{len(result)} \nMomo Product Name: {result[i]['ProductName']}, Momo Price: {result[i]['CurrentPrice']}")
            matchResult = db.ProductMatchV2(
                result[i]["ProductName"], result[i]["EnglishWords"], result[i]["ChineseWords"])
            # print(matchResult)
            if not matchResult:
                db.writeNoMatchResult(
                    result[i]["ProductID"])
            else:
                db.writeMatchResult(result[i]["ProductID"], matchResult["ProductID"],item['MyCate'])
                print(
                    f"PCHome ProductNick:{matchResult['ProductNick']}, PCHome Price:{matchResult['CurrentPrice']}")
   

