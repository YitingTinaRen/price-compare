import json
import os
import mysql.connector
from mysql.connector import errorcode
import config
from datetime import datetime





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



# Define tables
TABLES={}
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

TABLES['PCHomeProdCategory']=(
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
DB_NAME=config.DB_DB
mydb=mysql.connector.connect(
    host=config.DB_HOST,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
)

cursor=mydb.cursor()

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
                "(ProductID, ProductName, ProductNick, ProductDescription, CurrentPrice, ProductAvailability, ProductURL) "
                "VALUES (%(Id)s, %(Name)s, %(Nick)s, %(Slogan)s, %(P)s, %(ButtonType)s, %(url)s)")

add_pic = ("INSERT INTO PCHomePic"
            "(ProductID, PicURL) "
            "VALUES (%(Id)s, %(B)s)")

add_category = ("INSERT INTO PCHomeProdCategory"
                "(ProductID, CategoryCode, CategoryName, CategoryLevel) "
                "VALUES (%(Id)s, %(CateCode)s, %(CateName)s, %(CateLevel)s)")

update_products = ("UPDATE PCHomeProducts "
                   " SET ProductName = %(Name)s, ProductNick=%(Nick)s, ProductDescription=%(Slogan)s, CurrentPrice=%(P)s, ProductAvailability=%(ButtonType)s, ProductURL=%(url)s "
                   "WHERE ProductID=%(Id)s")
 
update_pic = ("UPDATE PCHomePic "
           "SET PicURL=%(B)s "
           "WHERE ProductID=%(Id)s")

update_category = ("UPDATE PCHomeProdCategory "
                   "SET CategoryCode=%(CateCode)s, CategoryName=%(CateName)s, CategoryLevel=%(CateLevel)s "
                   "WHERE ProductID=%(Id)s")


# Get PCHome txt file name list
abs_path = os.getcwd()
prodFileList = os.listdir(os.path.join(abs_path, "pchome-prod"))
desFileList = os.listdir(os.path.join(abs_path, "pchome-desc"))
saleFileList = os.listdir(os.path.join(abs_path, "pchome-salestatus"))

# prodFileList =["DAAO4F_prod.txt", "DAAO4J_prod.txt","DAAO5P_prod.txt","DAAO6U_prod.txt","DAAO7B_prod.txt","DAAO79_prod.txt"]
# desFileList = ["DAAO4F_desc.txt", "DAAO4J_desc.txt", "DAAO5P_desc.txt",
#                "DAAO6U_desc.txt", "DAAO7B_desc.txt", "DAAO79_desc.txt"]
# saleFileList = ["DAAO4F_salestatus.txt", "DAAO4J_salestatus.txt", "DAAO5P_salestatus.txt",
#                 "DAAO6U_salestatus.txt", "DAAO7B_salestatus.txt", "DAAO79_salestatus.txt"]

# Insert PChome Data to DB
cursor = mydb.cursor()
progress=0
for file in prodFileList:
    print(f'\nData processing progress: {progress}/{len(prodFileList)}')
    # Get current category code
    cateCode = file.split('_')[0]

    # Get PCHome data
    print(f'Read PCHome data with cateCode={cateCode}')
    if file.endswith(".txt"):
        prods = readFile("pchome-prod/"+file)
    else:
        print(f'Reading category {cateCode} prod file fails!')

    if cateCode+"_desc.txt" in desFileList:
        prodDesc = readFile("pchome-desc/"+cateCode+"_desc.txt")
    else:
        print(f'Reading category {cateCode} desc file fails!')

    if cateCode+"_salestatus.txt" in saleFileList:
        prodSale = readFile("pchome-salestatus/" +
                            cateCode+"_salestatus.txt")
    else:
        print(f'Reading category {cateCode} salestatus file fails!')

    addListProd = []
    updateListProd = []
    addListCate = []
    addListPic = []
    updateListPic = []
    # Organize data to fetch to the database
    for i in range(len(prods)-1):
        prod = {"Id": prods[i]['Id'], "Name": prods[i]['Name'], "Nick": prods[i]['Nick'], "P": prods[i]["Price"]["P"],
                "url": "https://24h.pchome.com.tw/prod/"+prods[i]["Id"][0:-4]}
        if prodSale:
            prod.update({"ButtonType": prodSale[i]["ButtonType"]})
        else:
            prod.update({"ButtonType": 'None'})
        if prodDesc:
            prod.update({"Slogan": prodDesc[prods[i]['Id'][0:-4]]["Slogan"]})
        else:
            prod.update({"Slogan":'None'})

        
        cursor.execute("select * from PCHomeProducts where ProductID=%s", (prod['Id'],))
        result=cursor.fetchone()
        if result:
            # Update existing data
            print(f'Update existing data, prodID={prods[i]["Id"]}')
            updateListProd.append(prod)
            if prods[i]["Pic"]["B"]:
                updateListPic.append({
                    "Id": prods[i]["Id"], "B": "https://cs-f.ecimg.tw"+prods[i]["Pic"]["B"]})
            else:
                updateListPic.append({
                    "Id": prods[i]["Id"], "B": "None"})
            
            cursor.execute("select ProductID, date_format(DateTime, '%Y%m%d')  from PCHomeProdCategory where ProductID=%s",
                            (prods[i]["Id"],))
            result = cursor.fetchall()
            if result:
                if result[0][1] <= str(int(datetime.strftime(datetime.now(), '%Y%m%d'))-1):
                    # Delete the data updated yesterday
                    cursor.execute(
                    "DELETE FROM PCHomeProdCategory WHERE ProductID = %s", (prods[i]["Id"],))
                    mydb.commit()

            cateList = list(prods[-1]["Category"])
            L1CategoryName = {"DECH": "嬰童", "DEAI": "婦幼",
                                "DEAU": "推車汽座", "DAAO": "尿布"}
            addListCate.append({
                "Id": prods[i]["Id"], "CateCode": prods[-1]["Category"]['L0CategoryCode'], "CateName": prods[-1]["Category"]['L0CategoryName'], "CateLevel": 0})
            addListCate.append({
                "Id": prods[i]["Id"], "CateCode": prods[-1]["Category"]['L1CategoryCode'], "CateName": prods[-1]["Category"]['L1CategoryName'], "CateLevel": 1})
            addListCate.append({
                "Id": prods[i]["Id"], "CateCode": prods[-1]["Category"]['L2CategoryCode'], "CateName": prods[-1]["Category"]['L2CategoryName'], "CateLevel": 2})
        
        else:
            # Add new data
            print(f'Add new data, prodID={prods[i]["Id"]}')
            addListProd.append(prod)
            if prods[i]["Pic"]["B"]:
                addListPic.append({
                    "Id": prods[i]["Id"], "B": "https://cs-f.ecimg.tw"+prods[i]["Pic"]["B"]})
            else:
                addListPic.append({
                    "Id": prods[i]["Id"], "B": "None"})
                
            cateList=list(prods[-1]["Category"])
            L1CategoryName={"DECH": "嬰童", "DEAI": "婦幼", "DEAU": "推車汽座", "DAAT": "濕紙巾", "DAAO": "尿布"}
            addListCate.append({
                "Id": prods[i]["Id"], "CateCode": prods[-1]["Category"]['L0CategoryCode'], "CateName": prods[-1]["Category"]['L0CategoryName'], "CateLevel": 0})
            addListCate.append({
                "Id": prods[i]["Id"], "CateCode": prods[-1]["Category"]['L1CategoryCode'], "CateName": prods[-1]["Category"]['L1CategoryName'], "CateLevel": 1})
            addListCate.append({
                "Id": prods[i]["Id"], "CateCode": prods[-1]["Category"]['L2CategoryCode'], "CateName": prods[-1]["Category"]['L2CategoryName'], "CateLevel": 2})
    print("Uploading data to DB")
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

    progress+=1

cursor.close()
mydb.close()


