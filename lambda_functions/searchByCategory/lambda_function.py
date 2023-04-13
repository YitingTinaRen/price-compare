import json
import os
import mysql.connector
from mysql.connector import errorcode
import random
import boto3


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

    def SearchProductbyCategory(CateLevel, CateName, ProdName):
        sql = """
            select P.ProductID, P.ProductName, P.CurrentPrice, P.ProductURL,C.CategoryName, P.EnglishWords, P.ChineseWords
            from MomoProdCategory as C
            inner join MomoProducts as P
            on C.ProductID=P.ProductID
            where C.CategoryLevel=%s and C.CategoryName like %s and P.ProductName like %s
            ;
            """
        val = (CateLevel, "%" + CateName + "%", "%" + ProdName + "%",)
        result = db.checkAllData(sql, val)
        return result


def send2SQS(data):
    randNum = int(1000 * random.random() % 1000)
    client = boto3.client('sqs')
    message = client.send_message(
        QueueUrl=os.environ['sqsUrl'],
        MessageBody=(
            json.dumps(data)
        ),
        MessageGroupId='momo-category',
        MessageDeduplicationId='momo-category' + str(randNum)
    )


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

    match_condition = json.loads(event['Records'][0]['body'])
    print(match_condition)

    result = db.SearchProductbyCategory(
        match_condition['CateLevel'],
        match_condition['CateName'],
        match_condition['ProdName'])

    for j in range(len(result)):
        print(
            f"\n\n{j}/{len(result)} \nMomo Product Name: {result[j]['ProductName']}, Momo Price: {result[j]['CurrentPrice']}")
        data = {
            "ProductName": result[j]["ProductName"],
            "EnglishWords": result[j]["EnglishWords"],
            "ChineseWords": result[j]["ChineseWords"],
            "MomoProductID": result[j]["ProductID"],
            "CateName": match_condition["CateName"],
            "MyCate": match_condition["MyCate"]
        }
        print(data)
        send2SQS(data)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
