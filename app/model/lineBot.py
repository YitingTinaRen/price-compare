from flask import *
import jwt
import requests
import config
from linebot import LineBotApi
from linebot.models import TextSendMessage


class lineBot:
    def sendmsg(token, msg):
        try:
            member = jwt.decode(token, config.PP_SECRET_KEY,
                                algorithms=config.PP_JWT_ALGO)
        except jwt.exceptions.InvalidTokenError as error:
            print(error)
            return jsonify({"error": True, "message": "Invalid token"}), 400

        # Get userID
        url = "https://api.line.me/v2/profile"
        res = requests.get(
            url,
            headers={
                "Authorization": "Bearer " +
                member["LineToken"]})
        res = res.json()
        userID = res['userId']
        line_bot_api = LineBotApi(config.Notify_channel_access_token)
        message = TextSendMessage(text=msg)
        line_bot_api.push_message(userID, message)
        return jsonify({"ok": True}), 200
