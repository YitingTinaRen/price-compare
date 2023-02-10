import mysql.connector
import config
from mysql.connector import errorcode

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

    def ProductMatch(ProdName):
        exluded_terms = ['系列']
        for terms in exluded_terms:
            ProdName = ProdName.replace(terms, "")
        ProdName = ProdName.replace("+", " ")
        # ProdName = ProdName.split('】')
        # ProdName[0] = ProdName[0].replace("【", "")
        # ProdName[1] = ProdName[1].replace("/", " ")
        # ProdName[1] = ProdName[1].replace("-", " ")
        
        if ProdName.find('】')==-1:
            l=[]
            if ProdName.find(' ')==-1:
                l.append(ProdName[:5])
                l.append(ProdName[6:])
            else:
                l.append(ProdName[:ProdName.index(' ')])
                l.append(ProdName[ProdName.index(' ')+1:])
                
            ProdName=l
        else:
            ProdName = ProdName.split('】')
            ProdName[0] = ProdName[0].replace("【", "")
        
        ProdName[1] = ProdName[1].replace("/", " ")
        ProdName[1] = ProdName[1].replace("-", " ")
        
        sql = """
            select ProductID, ProductName,ProductNick, CurrentPrice, ProductURL,
            match(ProductName, ProductNick) against(%s in natural language mode) as score 
            from PCHomeProducts 
            where match(ProductName, ProductNick) against(%s in natural language mode) > 10 
            and ProductID 
            in (select ProductID 
                from PCHomeProducts 
                where match(ProductName, ProductNick) against(%s in natural language mode))
            Limit 5;
            """
        val = (ProdName[1], ProdName[1], ProdName[0],)
        result = db.checkAllData(sql, val)
        # print(f'PCHome result: {result}')
        return result
    
    def ProductMatchV2(ProdName, English, Chinese):
        ProdName = ProdName.replace("+", " ")
        # ProdName = ProdName.split('】')
        # ProdName[0] = ProdName[0].replace("【", "")
        # ProdName[1] = ProdName[1].replace("/", " ")
        # ProdName[1] = ProdName[1].replace("-", " ")
        
        if ProdName.find('】')==-1:
            l=[]
            if ProdName.find(' ')==-1:
                l.append(ProdName[:5])
                l.append(ProdName[6:])
            else:
                l.append(ProdName[:ProdName.index(' ')])
                l.append(ProdName[ProdName.index(' ')+1:])
                
            ProdName=l
        else:
            ProdName = ProdName.split('】')
            ProdName[0] = ProdName[0].replace("【", "")
        
        ProdName[1] = ProdName[1].replace("/", " ")
        ProdName[1] = ProdName[1].replace("-", " ")
        
        sql = """
            select ProductID, ProductName,ProductNick, CurrentPrice, ProductURL
            from PCHomeProducts 
            where match(EnglishWords) against(%s in natural language mode)
            and match(ChineseWords) against(%s in natural language mode) 
            and ProductID 
            in (select ProductID 
                from PCHomeProducts 
                where match(ProductName, ProductNick) against(%s in natural language mode))
            ;
            """
        val = (English, Chinese, ProdName[0],)
        result = db.checkAllData(sql, val)
        # print(f'PCHome result: {result}')
        return result

    def SearchProductbyCategory(CateLevel,CateName):
        sql = """
select P.ProductID, P.ProductName, P.CurrentPrice, P.ProductURL,C.CategoryName, P.EnglishWords, P.ChineseWords 
from MomoProdCategory as C 
inner join MomoProducts as P 
on C.ProductID=P.ProductID 
where C.CategoryLevel=%s and C.CategoryName like %s and P.ProductName like %s 
            ;
            """
        val = (CateLevel,"%"+CateName+"%","%"+CateName+"%",)
        result = db.checkAllData(sql, val)
        return result
    
    def writeMatchResult(MomoProductID,PCHProductID, MyCate):
        sql="""
            update MomoProducts
            set PCHProductID=%s, HasMatching=TRUE, MyCategory=%s where ProductID = %s;
        """
        val=(PCHProductID, MyCate,MomoProductID,)
        result=db.writeData(sql,val)
        print(f'Table update result: {result}')
        return result

# class compare:
#     def matchMartsProducts(ProductList):
#         for item in ProductList
#         result=db.ProductMatch(ProdName)



if __name__ == '__main__':
    MyCate='餐椅'
    # result=db.SearchProductbyCategory('3',"固齒器")
    # result=db.SearchProductbyCategory('2',"水杯") #配對率頗低，錯誤率很高 Done
    # result=db.SearchProductbyCategory('3',"消毒") #可以拿來demo，但配對率還是需要改進 Done
    # result=db.SearchProductbyCategory('3',"圍欄") #可以demo Done
    # result=db.SearchProductbyCategory('3',"澡盆") # 不能用 沒配對成功的
    # result=db.SearchProductbyCategory('3',"汽座") #可以試試看，不過結果也沒很好
    result=db.SearchProductbyCategory('3',"餐椅") #可以
    # result=db.SearchProductbyCategory('3',"地墊") #
    # result=db.SearchProductbyCategory('3',"奶瓶") #
    # result=db.SearchProductbyCategory('3',"奶嘴") #
    # result=db.SearchProductbyCategory('3',"溫奶器") #
    # result=db.SearchProductbyCategory('3',"推車") #
    # !!!result=db.SearchProductbyCategory('3',"副食品") #C.CategoryLevel='2' and C.CategoryName like '%副食品%' and P.ProductName like '%副食品分裝盒%'


    
    removeIndex=[]
    for i in range(len(result)):
        print(f"\n\n{i}/{len(result)} \nMomo Product Name: {result[i]['ProductName']}, Momo Price: {result[i]['CurrentPrice']}")
        # matchResult=db.ProductMatch(result[i]["ProductName"])
        matchResult=db.ProductMatchV2(result[i]["ProductName"],result[i]["EnglishWords"], result[i]["ChineseWords"])
        print(matchResult)
        if not matchResult:
            removeIndex.append(i)
        else:
            db.writeMatchResult(result[i]["ProductID"], matchResult[0]["ProductID"],MyCate)
            print(
                f"PCHome ProductNick:{matchResult[0]['ProductNick']}, PCHome Price:{matchResult[0]['CurrentPrice']}")
   

