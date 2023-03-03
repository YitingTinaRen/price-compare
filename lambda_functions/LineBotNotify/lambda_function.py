from linebot import LineBotApi
from linebot.models import TextSendMessage
import mysql.connector
from mysql.connector import errorcode
import os
import requests
import json


def sendmsg(LineToken, msg):

    # Get userID
    url = "https://api.line.me/v2/profile"
    res = requests.get(url, headers={"Authorization": "Bearer "+LineToken})
    res = res.json()
    userID = res['userId']
    line_bot_api = LineBotApi(
        os.environ['Notify_channel_access_token'])
    message = TextSendMessage(text=msg)
    line_bot_api.push_message(userID, message)

def lambda_handler(event,context):
    # Connect to database
    mydb = mysql.connector.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_DB'],
    )
    cursor = mydb.cursor()

    # Read SQS msg
    data = json.loads(event['Records'][0]['body'])
    print(data)

    cursor = mydb.cursor(dictionary=True)
    for item in data:
        TrackingID=item[0]
        MemberID=item[1]
        sql="""
            select PT.TargetPrice, M.LineToken,P.ProductName
            from ProductTracking as PT
            inner join member as M
            on PT.MemberID=M.MemberID
            inner join MomoProducts as P
            on PT.MomoProductID = P.ProductID
            where PT.MemberID=%s and (PT.TrackingID=%s)
        """
        val=(MemberID,TrackingID,)
        cursor.execute(sql,val)
        data=cursor.fetchall()
        # print(data)
        msg=f'您追蹤的商品:{data[0]["ProductName"]}\n 已經低於${data[0]["TargetPrice"]}!'
        print(msg)
        sendmsg(data[0]["LineToken"],msg)
        
    cursor.close()
    mydb.close()

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


