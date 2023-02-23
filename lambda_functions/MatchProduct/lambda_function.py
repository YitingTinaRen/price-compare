import json
import os
import mysql.connector
from mysql.connector import errorcode
from operator import add


class db:
    def checkAllData(sql, val=()):
        # return data type is dictionary
        mydb = mysql.connector.connect(pool_name=os.environ['DB_POOL_NAME'])
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()  # fetch all data
        mycursor.close()
        mydb.close()
        return myresult

    def checkOneData(sql, val=()):
        # return data type is dictionary
        mydb = mysql.connector.connect(pool_name=os.environ['DB_POOL_NAME'])
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchone()  # fetch one data
        mycursor.close()
        mydb.close()
        return myresult

    def writeData(sql, val):
        try:
            mydb = mysql.connector.connect(
                pool_name=os.environ['DB_POOL_NAME'])
            mycursor = mydb.cursor()
            mycursor.execute(sql, val)
            mydb.commit()
            mycursor.close()
            mydb.close()
            return True
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            return False

    def ProductMatchV2(ProdName, English, Chinese, CateName):

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
            and match(ChineseWords) against(%s in boolean mode) >30
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
        print(f"matching result{result}")
        if result:
            Eng_point = []
            Chi_point = []
            for i in range(len(result)):
                print(
                    f'PCHome Product name:{result[i]["ProductName"]}, English match score:{result[i]["rel1"]}, Chinese match score:{result[i]["rel2"]}')
                Eng_point.append(len(list(set(result[i]['EnglishWords'].split(
                    ' ')).intersection(set(English.split(' '))))))
                Chi_point.append(len(list(set(result[i]['ChineseWords'].split(
                    ' ')).intersection(set(Chinese.split(' '))))))

            total_point = list(map(add, Eng_point, Chi_point))
            index = total_point.index(max(total_point))

            result = result[index]

        return result

    def writeMatchResult(MomoProductID, PCHProductID, MyCate):
        sql = """
            update MomoProducts
            set PCHProductID=%s, HasMatching=TRUE, MyCategory=%s where ProductID = %s;
        """
        val = (PCHProductID, MyCate, MomoProductID,)
        result = db.writeData(sql, val)
        print(f'Table update result: {result}')
        return result


def lambda_handler(event, context):

    # TODO implement
    # MySQL Database config
    dbconfig = {
        "host": os.environ['DB_HOST'],
        "user": os.environ['DB_USER'],
        "password": os.environ['DB_PASSWORD'],
        "database": os.environ['DB_DB']
    }

    # Create MySQL pooling
    mydb = mysql.connector.connect(
        pool_name=os.environ['DB_POOL_NAME'],
        pool_size=5,
        **dbconfig
    )
    mydb.close()

    result = json.loads(event['Records'][0]['body'])

    print(result)

    matchResult = db.ProductMatchV2(
        result["ProductName"], result["EnglishWords"], result["ChineseWords"], result['CateName'])
    if matchResult:
        db.writeMatchResult(
            result["MomoProductID"], matchResult["ProductID"], result['MyCate'])
        print(
            f"PCHome ProductNick:{matchResult['ProductNick']}, PCHome Price:{matchResult['CurrentPrice']}")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
