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

    def getResult(Category, Page):
        sql="""
            select M.ProductID, M.ProductName, M.CurrentPrice, M.ProductURL,
            P.ProductID as PCHProductID, P.ProductName as PCHProductName,P.CurrentPrice as PCHCurrentPrice, P.ProductURL as PCHProductURL,
            substring_index(group_concat(Pic.PicURL order by PCHPicID separator ','), ',',1) as PicURL
            from MomoProducts as M 
            inner join PCHomeProducts as P 
            on M.PCHProductID=P.ProductID 
            inner join MomoPic as Pic
            on M.ProductID=Pic.ProductID
            where M.MyCategory=%s and M.HasMatching =TRUE
            group by Pic.PicURL
            Limit 20 offset %s
        """

        val=(Category,Page,)
        result = db.checkAllData(sql,val)
        return result

    def getMomoBrand(Category):
        sql="""
            select ProductName
            from MomoProducts
            where MyCategory = %s
            and HasMatching=TRUE
        """

        val=(Category,)
        result = db.checkAllData(sql, val)
        return result

    def getResult_Brand(Category, Page, Brand):
        sql = """
            select M.ProductID, M.ProductName, M.CurrentPrice, M.ProductURL,
            P.ProductID as PCHProductID, P.ProductName as PCHProductName,P.CurrentPrice as PCHCurrentPrice, P.ProductURL as PCHProductURL,
            substring_index(group_concat(Pic.PicURL order by PCHPicID separator ','), ',',1) as PicURL
            from MomoProducts as M 
            inner join PCHomeProducts as P 
            on M.PCHProductID=P.ProductID 
            inner join MomoPic as Pic
            on M.ProductID=Pic.ProductID
            where M.MyCategory=%s and M.HasMatching =TRUE and M.ProductName like %s
            group by Pic.PicURL
            Limit 20 offset %s
        """

        val = (Category, '%'+Brand+'%',Page ,)
        result = db.checkAllData(sql, val)
        return result
    
    def checkMemberExist(email):
        sql="""
            select MemberID,Name,Email, date_format(TokenValidDate,'%Y-%m-%d') as TokenValidDate, LineToken
            from member
            where Email=%s
        """
        val=(email,)
        result = db.checkOneData(sql, val)
        return result

    def registerNewUser(Name, Picture, Email,Token):
        sql="""
            insert into member (Name, Picture, Email, TokenValidDate, LineToken)
            values(%s, %s, %s, date_add(current_date, interval 29 day), %s)
        """
        val=(Name, Picture, Email,Token,)
        result=db.writeData(sql,val)
        return result
    
    def updateUserInfo(Name,Picture, Email, Token):
        sql="""
            update member
            set Name=%s,
            Picture=%s,
            TokenValidDate=date_add(current_date, interval 29 day),
            Token=%s
            where Email=%s
        """
        val=(Name,Picture,Token,Email)
        result=db.writeData(sql,val)
        return result

    def getPCHPriceHistory(ID):
        sql="""
            select DATE_FORMAT(Date,'%Y-%m-%d') as Date, Price
            from PCHDaily_Price
            where ProductID = %s;
        """
        val=(ID,)
        result=db.checkAllData(sql,val)
        return result

    def getMomoPriceHistory(ID):
        sql = """
            select DATE_FORMAT(Date,'%Y-%m-%d') as Date, Price
            from MomoDaily_Price
            where ProductID = %s;
        """
        val = (ID,)
        result = db.checkAllData(sql, val)
        return result


