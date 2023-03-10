import re
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
    
    def updatePCHomeKeywords(data):
        sql="""
            UPDATE PCHomeProducts 
            SET EnglishWords=%(English)s, ChineseWords=%(Chinese)s 
            WHERE ProductID=%(ProductID)s
        """
        mydb = mysql.connector.connect(pool_name=config.DB_POOL_NAME)
        cursor = mydb.cursor()
        cursor.executemany(sql, data)
        mydb.commit()
        cursor.close()
        mydb.close()
    
    def updateMomoKeywords(data):
        sql="""
            UPDATE MomoProducts 
            SET EnglishWords=%(English)s, ChineseWords=%(Chinese)s 
            WHERE ProductID=%(ProductID)s
        """
        mydb = mysql.connector.connect(pool_name=config.DB_POOL_NAME)
        cursor = mydb.cursor()
        cursor.executemany(sql, data)
        mydb.commit()
        cursor.close()
        mydb.close()

    def SearchMomoProduct(Keyword):
        sql="""
            SELECT ProductID, ProductName 
            FROM MomoProducts
            WHERE ProductName like %s
        """
        val=("%"+Keyword+"%",)
        result=db.checkAllData(sql, val)
        return result
    
    def SearchPCHomeProduct(Keyword):
        sql="""
            SELECT ProductID, ProductName, ProductNick 
            FROM PCHomeProducts
            WHERE ProductName like %s or ProductNick like %s
        """
        val=("%"+Keyword+"%", "%"+Keyword+"%",)
        result=db.checkAllData(sql, val)
        return result




class Generator:
    def striphtml(data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
    def removeDuplicates(List):
        """remove duplicates in a list and return list"""
        return list(set(List))
    def splitEvery2Words(str):
        """return list of string"""
        newList=[]
        for i in range(0,len(str),2):
                newList.append(str[i:i+2])
        if len(newList[-1])==1:
            newList.pop(-1)
        return newList
    
    def split3Words(str):
        """return list of string"""
        subList=[]
        for i in range(len(str)-2):
            threeWords=str[i:i+3]
            rest=str.split(str[i:i+3])
            for sub in rest:
                if sub and len(sub)>1:
                    subList=subList+Generator.splitEvery2Words(sub)
            subList.append(threeWords)
            
        return subList


    def splitString(str):
        # remove html tag
        str=Generator.striphtml(str)
        # Filter out English words
        # EngList=re.sub(u"([^\u0041-\u007a])"," ",str).split(" ")
        EngList=re.sub(u"([^\u0030-\u007a])"," ",str).split(" ")
        EngList=Generator.removeDuplicates(EngList)
        EngList=list(filter(None, EngList))
        EngStr=' '.join(EngList)

        # Filter out Chinese words
        ChiList=re.sub(u"([^\u4e00-\u9fa5])"," ",str).split(" ")
        ChiList=Generator.removeDuplicates(ChiList)
        ChiList=list(filter(None,ChiList))
        newList=[]
        for item in ChiList:
            if len(item)>4:
                newList=newList+Generator.splitEvery2Words(item)
                newList=newList+Generator.split3Words(item)
        newList=Generator.removeDuplicates(newList)
        ChiList=ChiList+newList
        ChiStr=' '.join(ChiList)

        words={
            "English":EngStr,
            "Chinese":ChiStr
        }
        print(words)
        return words

        


if __name__ == '__main__':
    # Generator.splitString('中文 English 123 ABC 你好 12 34 56 想買麗貝樂尿布 <abs>kkk<rerg>')
    Keyword=["奶瓶","奶嘴","溫奶器","汽座","推車","副食品","副食品調理器","口水","水杯","地墊","餐椅","餐碗","餐盤","固齒器"]
    for item in Keyword:
        print(f'Keyword status: {item}')
        momoData=db.SearchMomoProduct(item)
        for i in range(len(momoData)):
            print(f'Spliting momo name! {i+1}/{len(momoData)}')
            NameWords=Generator.splitString(momoData[i]['ProductName'])
            momoData[i].update(NameWords)

        pchomeData=db.SearchPCHomeProduct(item)
        for i in range(len(pchomeData)):
            print(f'Spliting pchome name! {i+1}/{len(momoData)}')
            NameWords=Generator.splitString(pchomeData[i]['ProductName'])
            NickWords=Generator.splitString(pchomeData[i]['ProductNick'])
            NameWords["Chinese"]=NameWords["Chinese"]+NickWords["Chinese"]
            pchomeData[i].update(NameWords)

        print("Updating database:......")
        db.updatePCHomeKeywords(pchomeData)
        db.updateMomoKeywords(momoData)
        print("Complete updating database!")
