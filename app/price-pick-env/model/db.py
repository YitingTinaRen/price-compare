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
        try:
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()  # fetch all data
        except mysql.connector.Error as err:
            print(err.msg)
            return False
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
        ProdName = ProdName.split('】')
        ProdName[0] = ProdName[0].replace("【", "")
        ProdName[1] = ProdName[1].replace("/", " ")
        ProdName[1] = ProdName[1].replace("-", " ")

        # if ProdName.find('】')==-1:
        #     l=[]
        #     l.append(ProdName[:ProdName.index(' ')])
        #     l.append(ProdName[ProdName.index(' ')+1:])
        #     ProdName=l
        # else:
        #     ProdName = ProdName.split('】')
        #     ProdName[0] = ProdName[0].replace("【", "")

        # ProdName[1] = ProdName[1].replace("/", " ")
        # ProdName[1] = ProdName[1].replace("-", " ")

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

    def SearchProductbyCategory(CateLevel, CateName):
        sql = """
            select P.ProductID, P.ProductName, P.CurrentPrice, P.ProductURL,C.CategoryName 
            from MomoProdCategory as C 
            inner join MomoProducts as P 
            on C.ProductID=P.ProductID 
            where C.CategoryLevel=%s and C.CategoryName like %s 
            limit 20 offset 0;
            """
        val = (CateLevel, "%"+CateName+"%",)
        result = db.checkAllData(sql, val)
        return result

    def getResult(Category, Page):
        sql="""
            select M.ProductID, M.ProductName, M.CurrentPrice, M.ProductURL, 
            P.ProductID as PCHProductID, P.ProductName as PCHProductName,P.CurrentPrice as PCHCurrentPrice, P.ProductURL as PCHProductURL,
            Pic.PicURL 
            from MomoProducts as M 
            inner join PCHomeProducts as P 
            on M.PCHProductID=P.ProductID 
            inner join PCHomePic as Pic
            on P.ProductID=Pic.ProductID
            where M.MyCategory=%s and M.HasMatching =TRUE
            Limit 20 offset %s
        """

        val=(Category,Page,)
        result = db.checkAllData(sql,val)
        return result

