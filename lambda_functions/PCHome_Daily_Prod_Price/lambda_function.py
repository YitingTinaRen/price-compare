import json
import os
import mysql.connector


def lambda_handler(event, context):
    # TODO implement
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
        print(err)
        exit(1)
    cursor.close()

    add_data = """INSERT INTO PCHDaily_Price
                (ProductID, Price, Date)
                VALUES(%(Id)s, %(P)s, CURRENT_DATE)
    """

    content = json.loads(event['Records'][0]['body'])
    prods = content[0:len(content) - 3]
    print(prods)

    addListProd = []
    cursor = mydb.cursor()
    for i in range(len(prods) - 3):
        prod = {"Id": prods[i]['Id'], "P": prods[i]["Price"]["P"]}
        addListProd.append(prod)

    print("Uploading data to DB")
    cursor.executemany(add_data, addListProd)
    mydb.commit()
    cursor.close()
    mydb.close()

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
