import json
import boto3


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
    match_condition = [
        {'MyCate': '副食品分裝盒', 'CateName': '副食品',
            'ProdName': '副食品分裝盒%', 'CateLevel': '3'},
        {'MyCate': '固齒器', 'CateName': '固齒器',
            'ProdName': '固齒器', 'CateLevel': '3'},
        {'MyCate': '水杯', 'CateName': '水杯',
            'ProdName': '水杯', 'CateLevel': '2'},
        {'MyCate': '消毒鍋', 'CateName': '消毒',
            'ProdName': '消毒', 'CateLevel': '3'},
        {'MyCate': '圍欄', 'CateName': '圍欄',
         'ProdName': '圍欄', 'CateLevel': '3'},
        {'MyCate': '澡盆', 'CateName': '澡盆',
         'ProdName': '澡盆', 'CateLevel': '3'},
        {'MyCate': '汽座', 'CateName': '汽座',
         'ProdName': '汽座', 'CateLevel': '3'},
        {'MyCate': '餐椅', 'CateName': '餐椅',
         'ProdName': '餐椅', 'CateLevel': '3'},
        {'MyCate': '地墊', 'CateName': '地墊',
         'ProdName': '地墊', 'CateLevel': '3'},
        {'MyCate': '奶瓶', 'CateName': '奶瓶',
         'ProdName': '奶瓶', 'CateLevel': '3'},
        {'MyCate': '奶嘴', 'CateName': '奶嘴',
         'ProdName': '奶嘴', 'CateLevel': '3'},
        {'MyCate': '溫奶器', 'CateName': '溫奶器',
         'ProdName': '溫奶器', 'CateLevel': '3'},
        {'MyCate': '推車', 'CateName': '推車',
         'ProdName': '推車', 'CateLevel': '3'},
        {'MyCate': '副食品調理器', 'CateName': '調理',
         'ProdName': '調理', 'CateLevel': '3'},
        {'MyCate': '口水巾', 'CateName': '口水巾',
         'ProdName': '口水巾', 'CateLevel': '3'},
        {'MyCate': '圍兜', 'CateName': '圍兜',
         'ProdName': '圍兜', 'CateLevel': '3'},
        {'MyCate': '餐椅', 'CateName': '餐椅',
         'ProdName': '餐椅', 'CateLevel': '3'},
        {'MyCate': '餐碗', 'CateName': '餐具',
         'ProdName': '餐碗', 'CateLevel': '3'},
        {'MyCate': '餐盤', 'CateName': '餐具',
         'ProdName': '餐盤', 'CateLevel': '3'},
    ]
    for item in match_condition:
        send2SQS(item)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
