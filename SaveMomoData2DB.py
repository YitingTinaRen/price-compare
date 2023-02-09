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
    "`MyCategory varchar(25) default null,"
    "INDEX (`ProductID`), "
    "FOREIGN KEY (`PCHProductID`) REFERENCES `PCHomeProducts` (`ProductID`) ON DELETE CASCADE "
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
add_products = ("INSERT INTO MomoProducts"
                "(ProductID, ProductName, CurrentPrice, ProductSalecount, ProductURL, Event) "
                "VALUES (%(Id)s, %(Name)s, %(Price)s, %(Salecount)s, %(Url)s, %(Event)s)")

add_pic = ("INSERT INTO MomoPic"
           "(ProductID, PicURL) "
           "VALUES (%(Id)s, %(Pic)s)")

add_category = ("INSERT INTO MomoProdCategory"
                "(ProductID, CategoryCode, CategoryName, CategoryLevel) "
                "VALUES (%(Id)s, %(CateCode)s, %(CateName)s, %(CateLevel)s)")

update_products = ("UPDATE MomoProducts "
                   " SET ProductName = %(Name)s, CurrentPrice=%(Price)s, ProductSalecount=%(Salecount)s, ProductURL=%(Url)s, Event=%(Event)s "
                   "WHERE ProductID=%(Id)s")

update_pic = ("UPDATE MomoPic "
              "SET PicURL=%(Pic)s "
              "WHERE ProductID=%(Id)s")

update_category = ("UPDATE MomoProdCategory "
                   "SET CategoryCode=%(CateCode)s, CategoryName=%(CateName)s, CategoryLevel=%(CateLevel)s "
                   "WHERE ProductID=%(Id)s")

# Get momo txt file name list
abs_path=os.getcwd()
prodFileList = os.listdir(os.path.join(abs_path, "momo-prod"))

# Insert momo Data to DB
cursor = mydb.cursor()
progress = 0
for file in prodFileList:
    print(f'\nData processing progress: {progress}/{len(prodFileList)}')
    # Get current category code
    cateCode = prodFileList[0].split("-")[-1].split(".")[0]

    # Get momo data
    print(f'Read momo data with cateCode={cateCode}')
    if file.endswith(".txt"):
        prods = readFile("momo-prod/"+file)
    else:
        print(f'Reading category {cateCode} prod file fails!')

    addListProd = []
    updateListProd = []
    addListCate = []
    addListPic = []
    updateListPic = []
    # Organize data to fetch to the database
    for i in range(len(prods)-1):
        prod = {"Id": prods[i]['Id'], "Name": prods[i]['Name'], "Price": int(prods[i]["Price"].replace(',','')),
                "Url": "https://m.momoshop.com.tw"+prods[i]["Url"], "Event":prods[i]["Event"], "Salecount":prods[i]["Salecount"]}

        cursor.execute(
            "select * from MomoProducts where ProductID=%s", (prod['Id'],))
        result = cursor.fetchone()
        if result:
            # Update existing data
            print(f'Update existing data, prodID={prod["Id"]}')
            updateListProd.append(prod)

            if prods[i]["Pic"]:
                for picLink in prods[i]["Pic"]:
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
            cateList = list(prods[-1]["Category"])
            for j in range(int(len(cateList)/2)):
                addListCate.append({
                    "Id": prods[i]["Id"], "CateCode": prods[-1]["Category"][cateList[2*j]], "CateName": prods[-1]["Category"][cateList[2*j+1]], "CateLevel": int(cateList[2*j][1])})

        else:
            # Add new data
            print(f'Add new data, prodID={prods[i]["Id"]}')
            cursor.execute(add_products, prod)
            mydb.commit()
            if prods[i]["Pic"]:
                for picLink in prods[i]["Pic"]:
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
    progress +=1
cursor.close()
mydb.close()
