from flask import *
import model

api_linebot=Blueprint('api_linebot',__name__)


@api_linebot.route("/api/sendmsg", methods=['GET'])
def sendmsg():
    token=request.cookies.get('user')
    # result=model.lineBot.sendmsg(token)
    return result

