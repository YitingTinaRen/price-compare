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

    def getResult4Member(Category,Page,memberID):
        sql="""
            select M.ProductID, M.ProductName, M.CurrentPrice, M.ProductURL,
            P.ProductID as PCHProductID, P.ProductName as PCHProductName,P.CurrentPrice as PCHCurrentPrice, P.ProductURL as PCHProductURL,
            substring_index(group_concat(Pic.PicURL order by PCHPicID separator ','), ',',1) as PicURL,
            T.TrackingID, T.MemberID
            from MomoProducts as M 
            inner join PCHomeProducts as P 
            on M.PCHProductID=P.ProductID 
            inner join MomoPic as Pic
            on M.ProductID=Pic.ProductID
            left join (select MomoProductID, MemberID, TrackingID from ProductTracking where MemberID =%s) as T
            on M.ProductID=T.MomoProductID
            where M.MyCategory=%s and M.HasMatching =TRUE
            group by Pic.PicURL
            Limit 20 offset %s
        """
        val = (memberID, Category, Page, )
        result = db.checkAllData(sql, val)
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
    
    def getResult_Brand4member(Category, Page, Brand,memberID):
        sql = """
            select M.ProductID, M.ProductName, M.CurrentPrice, M.ProductURL,
            P.ProductID as PCHProductID, P.ProductName as PCHProductName,P.CurrentPrice as PCHCurrentPrice, P.ProductURL as PCHProductURL,
            substring_index(group_concat(Pic.PicURL order by PCHPicID separator ','), ',',1) as PicURL,
            T.TrackingID, T.MemberID
            from MomoProducts as M 
            inner join PCHomeProducts as P 
            on M.PCHProductID=P.ProductID 
            inner join MomoPic as Pic
            on M.ProductID=Pic.ProductID
            left join (select MomoProductID, MemberID, TrackingID from ProductTracking where MemberID =%s) as T
            on M.ProductID=T.MomoProductID
            where M.MyCategory=%s and M.HasMatching =TRUE and M.ProductName like %s
            group by Pic.PicURL
            Limit 20 offset %s
        """

        val = (memberID, Category, '%'+Brand+'%', Page,)
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
            select DATE_FORMAT(STR_TO_DATE(CONCAT(W.WeekNum, '1'), '%X%V%w'),'%Y-%m-%d') AS Date, MIN(W.Min_Price) as Price, W.ProductID
            from PCHWeekly_Price as W
            where W.ProductID=%s
            group by W.ProductID, Date
            union
            select DATE_FORMAT(D.Date,'%Y-%m-%d') AS Date, D.Price, D.ProductID
            from PCHDaily_Price as D
            where D.ProductID=%s and D.Date > (select MAX(DATE_FORMAT(STR_TO_DATE(CONCAT(WeekNum, '1'), '%X%V%w'),'%Y-%m-%d')) as Date
            from PCHWeekly_Price
            where ProductID=%s)
            order by Date;
        """
        val=(ID,ID,ID,)
        result=db.checkAllData(sql,val)
        return result

    def getMomoPriceHistory(ID):
        sql = """
            select DATE_FORMAT(STR_TO_DATE(CONCAT(W.WeekNum, '1'), '%X%V%w'),'%Y-%m-%d') AS Date, MIN(W.Min_Price) as Price, W.ProductID
            from MomoWeekly_Price as W
            where W.ProductID=%s
            group by W.ProductID, Date
            union
            select DATE_FORMAT(D.Date,'%Y-%m-%d') AS Date, D.Price, D.ProductID
            from MomoDaily_Price as D
            where D.ProductID=%s and D.Date > (select MAX(DATE_FORMAT(STR_TO_DATE(CONCAT(WeekNum, '1'), '%X%V%w'),'%Y-%m-%d')) as Date
            from MomoWeekly_Price
            where ProductID=%s)
            order by Date;
        """
        val = (ID,ID,ID,)
        result = db.checkAllData(sql, val)
        return result
    
    def TrackProduct(MemberID, MomoProductID, PCHProductID, TargetPrice, Notify):
        sql="""
            insert into ProductTracking (MemberID,MomoProductID, PCHProductID, TargetPrice, NotifyBelowTarget)
            values(%s, %s, %s, %s,%s)
        """
        val = (MemberID, MomoProductID, PCHProductID, TargetPrice, Notify,)
        result=db.writeData(sql,val)
        return result
    
    def UnTrackProduct(MomoProductID, PCHProductID, MemberID):
        sql = """
            delete from ProductTracking 
            where MomoProductID =%s and PCHProductID=%s and MemberID=%s
        """
        val = (MomoProductID, PCHProductID, MemberID)
        result = db.writeData(sql, val)
        return result
    
    def GetMemberTrackingProduct(MemberID,Page):
        sql = """
            select M.ProductID, M.ProductName, M.CurrentPrice, M.ProductURL,
            P.ProductID as PCHProductID, P.ProductName as PCHProductName,P.CurrentPrice as PCHCurrentPrice, P.ProductURL as PCHProductURL,
            substring_index(group_concat(Pic.PicURL order by PCHPicID separator ','), ',',1) as PicURL,
            T.TrackingID, T.MemberID, T.NotifyBelowTarget, T.TargetPrice,
            Mem.Name, Mem.Email, Mem.Picture as ProfilePic
            from MomoProducts as M 
            inner join PCHomeProducts as P 
            on M.PCHProductID=P.ProductID 
            inner join MomoPic as Pic
            on M.ProductID=Pic.ProductID
            right join (select MomoProductID, MemberID, TrackingID, NotifyBelowTarget, TargetPrice from ProductTracking where MemberID =%s) as T
            on M.ProductID=T.MomoProductID
            inner join member as Mem
            on Mem.MemberID=T.MemberID
            where M.HasMatching =TRUE  
            group by Pic.PicURL
            Limit 20 offset %s;
        """
        val = (MemberID,Page,)
        result = db.checkAllData(sql, val)
        return result
    
    def getMemberInfoOnly(MemberID):
        sql="""
            select Name, Picture as ProfilePic, Email
            from member
            where MemberID=%s
        """
        val=(MemberID,)
        result=db.checkOneData(sql,val)
        return result

    def setNotify(MemberID, TrackingID, TargetPrice):
        sql="""
            update ProductTracking
            set
            TargetPrice =%s,
            NotifyBelowTarget=TRUE
            where MemberID=%s and TrackingID=%s
        """
        val=(TargetPrice, MemberID, TrackingID,)
        result=db.writeData(sql,val)
        return result

    def cancelNotify(MemberID,TrackingID):
        sql="""
            update ProductTracking
            set TargetPrice=NULL,
            NotifyBelowTarget=FALSE
            where MemberID=%s and TrackingID=%s
        """
        val=(MemberID, TrackingID,)
        result=db.writeData(sql,val)
        return result

    def checkTargetPrice(TargetPrice,TrackingID):
        sql="""
            select M.CurrentPrice, P.CurrentPrice
            from ProductTracking as PT
            inner join MomoProducts as M
            on PT.MomoProductID=M.ProductID
            inner join PCHomeProducts as P
            on PT.PCHProductID=P.ProductID
            where PT.TrackingID=%s 
            and (M.CurrentPrice <= %s or P.CurrentPrice <= %s)
        """
        val=(TrackingID, TargetPrice, TargetPrice,)
        result=db.checkAllData(sql,val)
        return result
