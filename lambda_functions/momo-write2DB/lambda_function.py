import json
import os
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import re
import random
import boto3


def lambda_handler(event, context):

    # TODO implement
    # Define tables
    TABLES = {}
    TABLES['MomoProducts'] = (
        "CREATE TABLE `MomoProducts` ("
        "`MomoMainID` bigint not null auto_increment primary key,"
        "`ProductID` varchar(25) not null unique,"
        "`ProductName` varchar(255) not null,"
        "`CurrentPrice` int not null,"
        "`ProductSalecount` varchar(20) default 'None',"
        "`ProductURL` varchar(100) not null,"
        "`Event` varchar(50) default 'None',"
        "`DateTime` DATETIME default CURRENT_TIMESTAMP,"
        "`PCHProductID` varchar(25) default null, "
        "`HasMatching` boolean not null default FALSE, "
        "`MyCategory` varchar(25) default null,"
        "`EnglishWords` varchar(40) default null,"
        "`ChineseWords` varchar(5000) default null, "
        "`NumberWords` varchar(40) default null, "
        "INDEX (`ProductID`), "
        "FOREIGN KEY (`PCHProductID`) REFERENCES `PCHomeProducts` (`ProductID`) ON DELETE CASCADE "
        "FULLTEXT `keywords_index` (`EnglishWords`), "
        "FULLTEXT `keywords_index` (`ChineseWords`), "
        "FULLTEXT `keywords_index` (`NumberWords`), "
        "FULLTEXT `fulltext_index` (`ProductName`) "
        ") ENGINE=InnoDB CHARACTER SET = utf8mb4")

    TABLES['MomoPic'] = (
        "CREATE TABLE `MomoPic` ("
        "`MomoPicID` bigint not null auto_increment primary key,"
        " `ProductID` varchar(25) not null,"
        " `PicURL` varchar(100) not null,"
        " `DateTime` DATETIME default CURRENT_TIMESTAMP,"
        " FOREIGN KEY (`ProductID`) REFERENCES `MomoProducts` (`ProductID`) ON DELETE CASCADE "
        ") ENGINE=InnoDB CHARACTER SET = utf8mb4")

    TABLES['MomoProdCategory'] = (
        "CREATE TABLE `MomoProdCategory` ("
        "`MomoCateID` bigint not null auto_increment primary key,"
        " `ProductID` varchar(25) not null,"
        " `CategoryCode` varchar(10) not null,"
        " `CategoryName` varchar(20) not null,"
        " `CategoryLevel` int(10) not null,"
        " `DateTime` DATETIME default CURRENT_TIMESTAMP,"
        " FOREIGN KEY (`ProductID`) REFERENCES `MomoProducts` (`ProductID`) ON DELETE CASCADE "
        ") ENGINE=InnoDB CHARACTER SET = utf8mb4")

    # Connect to database
    DB_NAME = os.environ['DB_DB']
    mydb = mysql.connector.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
    )
    cursor = mydb.cursor()

    # Create database
    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            mydb.database = DB_NAME
        else:
            print(err)
            exit(1)

    # Create tables
    for table_name in TABLES:
        table_description = TABLES[table_name]
        # print(table_description)
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

    cursor.close()

    # Define data insertion statement
    add_products = ("INSERT INTO MomoProducts"
                    "(ProductID, ProductName, CurrentPrice, ProductSalecount, ProductURL, Event, EnglishWords, ChineseWords) "
                    "VALUES (%(Id)s, %(Name)s, %(Price)s, %(Salecount)s, %(Url)s, %(Event)s,%(English)s,%(Chinese)s)")

    add_pic = ("INSERT INTO MomoPic"
               "(ProductID, PicURL) "
               "VALUES (%(Id)s, %(Pic)s)")

    add_category = ("INSERT INTO MomoProdCategory"
                    "(ProductID, CategoryCode, CategoryName, CategoryLevel) "
                    "VALUES (%(Id)s, %(CateCode)s, %(CateName)s, %(CateLevel)s)")

    update_products = ("UPDATE MomoProducts "
                       " SET ProductName = %(Name)s, CurrentPrice=%(Price)s, ProductSalecount=%(Salecount)s, ProductURL=%(Url)s, Event=%(Event)s, EnglishWords=%(English)s, ChineseWords=%(Chinese)s "
                       "WHERE ProductID=%(Id)s")

    update_pic = ("UPDATE MomoPic "
                  "SET PicURL=%(Pic)s "
                  "WHERE ProductID=%(Id)s")

    # Read SQS msg
    prods = json.loads(event['Records'][0]['body'])
    print(prods)

    addListProd = []
    updateListProd = []
    addListCate = []
    addListPic = []
    updateListPic = []
    cursor = mydb.cursor()
    # Organize data to fetch to the database
    for i in range(len(prods)-1):
        prod = {"Id": prods[i]['Id'], "Name": prods[i]['Name'],  "Price": prods[i]["Price"],
                "Url": "https://m.momoshop.com.tw"+prods[i]["Url"], "Event": prods[i]["Event"], "Salecount": prods[i]["Salecount"]}
        NameWords = Generator.splitString(prod['Name'])
        prod.update(NameWords)
        cursor.execute(
            "select TrackingID, MemberID from ProductTracking where MomoProductID=%s and TargetPrice>=%s", (prods[i]['Id'], prods[i]["Price"],))
        result = cursor.fetchall()
        if result:
            send2SQS(result)
        cursor.execute(
            "select * from MomoProducts where ProductID=%s", (prod['Id'],))
        result = cursor.fetchone()
        if result:
            # Update existing data
            print(f'Update existing data, prodID={prod["Id"]}')
            updateListProd.append(prod)

            if prods[i]["Pic"]:
                for picLink in prods[i]["Pic"]:
                    print(
                        f'update ProductID: {prods[i]["Id"]}, Pic: {picLink}')
                    updateListPic.append({
                        "Id": prods[i]["Id"], "Pic": picLink})
            else:
                updateListPic.append({
                    "Id": prods[i]["Id"], "Pic": "None"})

            cursor.execute("select ProductID, date_format(DateTime, '%Y%m%d')  from MomoProdCategory where ProductID=%s",
                           (prods[i]["Id"],))
            result = cursor.fetchall()
            if result:
                if result[0][1] <= str(int(datetime.strftime(datetime.now(), '%Y%m%d'))-1):
                    # Delete the data updated yesterday
                    cursor.execute(
                        "DELETE FROM MomoProdCategory WHERE ProductID = %s", (prods[i]["Id"],))
                    mydb.commit()
        else:
            # Add new data
            print(f'Add new data, prodID={prods[i]["Id"]}')
            cursor.execute(add_products, prod)
            mydb.commit()
            if prods[i]["Pic"]:
                for picLink in prods[i]["Pic"]:
                    print(
                        f'Append ProductID: {prods[i]["Id"]}, Pic: {picLink}')
                    addListPic.append({
                        "Id": prods[i]["Id"], "Pic": picLink})
            else:
                addListPic.append({
                    "Id": prods[i]["Id"], "Pic": "None"})

        cateList = list(prods[-1]["Category"])
        for j in range(int(len(cateList)/2)):
            addListCate.append({
                "Id": prods[i]["Id"], "CateCode": prods[-1]["Category"][cateList[2*j]], "CateName": prods[-1]["Category"][cateList[2*j+1]], "CateLevel": int(cateList[2*j][1])})
    print("Uploading data to DB")

    cursor.fast_executemany = True
    cursor.executemany(update_products, updateListProd)
    mydb.commit()
    cursor.executemany(add_products, addListProd)
    mydb.commit()
    print(f'updateListPic:{updateListPic}')
    cursor.executemany(update_pic, updateListPic)
    mydb.commit()
    print(f'addListPic:{addListPic}')
    cursor.executemany(add_pic, addListPic)
    mydb.commit()
    cursor.executemany(add_category, addListCate)
    mydb.commit()

    cursor.close()
    mydb.close()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def send2SQS(data):
    randNum = int(1000*random.random() % 1000)
    client = boto3.client('sqs')
    message = client.send_message(
        QueueUrl=os.environ['sqsUrl'],
        MessageBody=(
            json.dumps(data)
        ),
        MessageGroupId='momo-category',
        MessageDeduplicationId='momo-category' + str(randNum)
    )

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


class Generator:
    def striphtml(data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)

    def removeDuplicates(List):
        """remove duplicates in a list and return list"""
        return list(set(List))

    def splitEvery2Words(str):
        """return list of string"""
        newList = []
        for i in range(0, len(str), 2):
            newList.append(str[i:i+2])
        if len(newList[-1]) == 1:
            newList.pop(-1)
        return newList

    def split3Words(str):
        """return list of string"""
        subList = []
        for i in range(len(str)-2):
            threeWords = str[i:i+3]
            rest = str.split(str[i:i+3])
            for sub in rest:
                if sub and len(sub) > 1:
                    subList = subList+Generator.splitEvery2Words(sub)
            subList.append(threeWords)

        return subList

    def splitString(str):
        # remove html tag
        str = Generator.striphtml(str)
        # Filter out English words
        # EngList=re.sub(u"([^\u0041-\u007a])"," ",str).split(" ")
        EngList = re.sub(u"([^\u0030-\u007a])", " ", str).split(" ")
        EngList = Generator.removeDuplicates(EngList)
        EngList = list(filter(None, EngList))
        EngStr = ' '.join(EngList)

        # Filter out Chinese words
        ChiList = re.sub(u"([^\u4e00-\u9fa5])", " ", str).split(" ")
        ChiList = Generator.removeDuplicates(ChiList)
        ChiList = list(filter(None, ChiList))
        newList = []
        for item in ChiList:
            if len(item) > 4:
                newList = newList+Generator.splitEvery2Words(item)
                newList = newList+Generator.split3Words(item)
        newList = Generator.removeDuplicates(newList)
        ChiList = ChiList+newList
        ChiStr = ' '.join(ChiList)

        words = {
            "English": EngStr,
            "Chinese": ChiStr
        }
        print(words)
        return words
