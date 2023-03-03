import json
import os
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import re
import boto3
import random


def lambda_handler(event, context):
    # TODO implement

    # Define tables
    TABLES = {}
    TABLES['PCHomeProducts'] = (
        "CREATE TABLE `PCHomeProducts` ("
        "`PCHMainID` bigint not null auto_increment primary key,"
        "`ProductID` varchar(25) not null unique,"
        "`ProductName` varchar(255) not null,"
        "`ProductNick` varchar(255) not null,"
        "`ProductDescription` varchar(3000) default 'NONE',"
        "`CurrentPrice` int not null,"
        "`ProductAvailability` varchar(20) not null,"
        "`ProductURL` varchar(100) not null,"
        "`DateTime` DATETIME default CURRENT_TIMESTAMP,"
        "`EnglishWords` varchar(40) default null,"
        "`ChineseWords` varchar(5000) default null, "
        "`NumberWords` varchar(40) default null, "
        "FULLTEXT `fulltext_index` (`ProductName`, `ProductNick`),"
        "FULLTEXT `keywords_index` (`EnglishWords`), "
        "FULLTEXT `keywords_index` (`ChineseWords`), "
        "FULLTEXT `keywords_index` (`NumberWords`), "
        "INDEX (`ProductID`) "
        ") ENGINE=InnoDB CHARACTER SET = utf8mb4")

    TABLES['PCHomePic'] = (
        "CREATE TABLE `PCHomePic` ("
        "`PCHPicID` bigint not null auto_increment primary key,"
        " `ProductID` varchar(25) not null,"
        " `PicURL` varchar(100) not null,"
        " `DateTime` DATETIME default CURRENT_TIMESTAMP,"
        " FOREIGN KEY (`ProductID`) REFERENCES `PCHomeProducts` (`ProductID`) ON DELETE CASCADE "
        ") ENGINE=InnoDB CHARACTER SET = utf8mb4")

    TABLES['PCHomeProdCategory'] = (
        "CREATE TABLE `PCHomeProdCategory` ("
        "`PCHCateID` bigint not null auto_increment primary key,"
        " `ProductID` varchar(25) not null,"
        " `CategoryCode` varchar(10) not null,"
        " `CategoryName` varchar(20) not null,"
        " `CategoryLevel` int(10) not null,"
        " `DateTime` DATETIME default CURRENT_TIMESTAMP,"
        " FOREIGN KEY (`ProductID`) REFERENCES `PCHomeProducts` (`ProductID`) ON DELETE CASCADE "
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
    add_products = ("INSERT INTO PCHomeProducts"
                    "(ProductID, ProductName, ProductNick, ProductDescription, CurrentPrice, ProductAvailability, ProductURL, EnglishWords,ChineseWords) "
                    "VALUES (%(Id)s, %(Name)s, %(Nick)s, %(Slogan)s, %(P)s, %(ButtonType)s, %(url)s, %(English)s, %(Chinese)s)")

    add_pic = ("INSERT INTO PCHomePic"
            "(ProductID, PicURL) "
            "VALUES (%(Id)s, %(B)s)")

    add_category = ("INSERT INTO PCHomeProdCategory"
                    "(ProductID, CategoryCode, CategoryName, CategoryLevel) "
                    "VALUES (%(Id)s, %(CateCode)s, %(CateName)s, %(CateLevel)s)")

    update_products = ("UPDATE PCHomeProducts "
                    " SET ProductName = %(Name)s, ProductNick=%(Nick)s, ProductDescription=%(Slogan)s, CurrentPrice=%(P)s, ProductAvailability=%(ButtonType)s, ProductURL=%(url)s, EnglishWords=%(English)s, ChineseWords=%(Chinese)s "
                    "WHERE ProductID=%(Id)s")

    update_pic = ("UPDATE PCHomePic "
                "SET PicURL=%(B)s "
                "WHERE ProductID=%(Id)s")

    update_category = ("UPDATE PCHomeProdCategory "
                    "SET CategoryCode=%(CateCode)s, CategoryName=%(CateName)s, CategoryLevel=%(CateLevel)s "
                    "WHERE ProductID=%(Id)s")


    # Read SQS msg
    #print(event['Records'][0]['body'])
    # content=json.loads(json.dumps(event['Records'][0]['body']))
    content=json.loads(event['Records'][0]['body'])
    prods = content[0:len(content)-3]
    print(content[-1])
    print(content[-2])
    prodDesc = content[-1]['description']
    print(f'prodDesc:{prodDesc}')
    prodSale = content[-2]['salestatus']

    # Insert PChome Data to DB
    addListProd = []
    updateListProd = []
    addListCate = []
    addListPic = []
    updateListPic = []
    
    cursor = mydb.cursor()
    # Organize data to fetch to the database
    for i in range(len(prods)-3):
        prod = {"Id": prods[i]['Id'], "Name": prods[i]['Name'], "Nick": prods[i]['Nick'], "P": prods[i]["Price"]["P"],
                "url": "https://24h.pchome.com.tw/prod/"+prods[i]["Id"][0:-4]}
        NameWords=Generator.splitString(prod['Name'])
        NickWords=Generator.splitString(prod['Nick'])
        NameWords["Chinese"]=NameWords["Chinese"]+' '+NickWords["Chinese"]
        NameWords["Chinese"]=' '.join(set(NameWords["Chinese"].split(' ')))
        prod.update(NameWords)

        cursor.execute(
            "select TrackingID, MemberID from ProductTracking where PCHProductID=%s and TargetPrice<=%s", (prods[i]['Id'], prods[i]["Price"]["P"],))
        result = cursor.fetchall()
        if result:
            send2SQS(result)

        if prodSale:
            prod.update({"ButtonType": prodSale[i]["ButtonType"]})
        else:
            prod.update({"ButtonType": 'None'})
        if prodDesc:
            prod.update({"Slogan": prodDesc[0][prod['Id'][0:-4]]["Slogan"]})
        else:
            prod.update({"Slogan": 'None'})

        cursor.execute(
            "select * from PCHomeProducts where ProductID=%s", (prod['Id'],))
        result = cursor.fetchone()
        if result:
            # Update existing data
            print(f'Update existing data, prod={prod}')
            updateListProd.append(prod)
            if prods[i]["Pic"]["B"]:
                updateListPic.append({
                    "Id": prod["Id"], "B": "https://cs-f.ecimg.tw"+prods[i]["Pic"]["B"]})
            else:
                updateListPic.append({
                    "Id": prod["Id"], "B": "None"})

            cursor.execute("select ProductID, date_format(DateTime, '%Y%m%d')  from PCHomeProdCategory where ProductID=%s",
                           (prod["Id"],))
            result = cursor.fetchall()
            if result:
                if result[0][1] <= str(int(datetime.strftime(datetime.now(), '%Y%m%d'))-1):
                    # Delete the data updated yesterday
                    cursor.execute(
                        "DELETE FROM PCHomeProdCategory WHERE ProductID = %s", (prod["Id"],))
                    mydb.commit()
        else:
            # Add new data
            print(f'Add new data, prodID={prods[i]["Id"]}')
            addListProd.append(prod)
            if prods[i]["Pic"]["B"]:
                addListPic.append({
                    "Id": prod["Id"], "B": "https://cs-f.ecimg.tw"+prods[i]["Pic"]["B"]})
            else:
                addListPic.append({
                    "Id": prod["Id"], "B": "None"})

        # handle category
        #print(content[-3])
        addListCate.append({
            "Id": prod["Id"], "CateCode": content[-3]['L0CategoryCode'], "CateName": content[-3]['L0CategoryName'], "CateLevel": 0})
        addListCate.append({
            "Id": prod["Id"], "CateCode": content[-3]['L1CategoryCode'], "CateName": content[-3]['L1CategoryName'], "CateLevel": 1})
        addListCate.append({
            "Id": prod["Id"], "CateCode": content[-3]['L2CategoryCode'], "CateName": content[-3]['L2CategoryName'], "CateLevel": 2})
    
    print("Uploading data to DB")
    cursor.fast_executemany = True
    cursor.executemany(update_products, updateListProd)
    mydb.commit()
    cursor.executemany(add_products, addListProd)
    mydb.commit()
    cursor.executemany(update_pic, updateListPic)
    mydb.commit()
    cursor.executemany(add_pic, addListPic)
    mydb.commit()
    cursor.executemany(add_category, addListCate)
    mydb.commit()

    cursor.close()
    mydb.close()

    return {
        'statusCode': 200,
        'body': json.dumps(f'Category code: {content[-3]["L2CategoryCode"]}, Category name:{content[-3]["L2CategoryName"]} updates to DB successfully!')
    }

def readFile(relative_path):
    """
    relative_path ="pchome-prod/DAAO00_prod.txt"
    return data
    """
    abs_path=os.getcwd()
    full_path=os.path.join(abs_path, relative_path)
    
    with open(full_path, 'r') as f:
        json_data=f.read()
        data = json.loads(json_data)
    
    return data

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
