from flask import *
import model
import random
import config
import requests
from urllib.parse import urlencode, quote
import jwt
from datetime import date, timedelta, datetime

stateList = []

class member:
    def login():
        randNum = str(int(10000*random.random() % 10000))
        stateList.append(randNum)
        content = {
            "client_id": config.client_id,
            "redirect_uri": config.call_back,
            "state": randNum,
            "scope": "profile email openid",
            "switch_amr": "true"
        }
        authURL = "https://access.line.me/oauth2/v2.1/authorize?response_type=code&" + \
            urlencode(content, quote_via=quote)
        
        return authURL

    def callback(code,state,error_desc,error_code):
        if error_code:
            return jsonify({"error": True, "errormsg": f"Error code: {error_code}, error description{error_desc}"})
        # Check state is in the stateList
        if state in stateList:
            # Request token in order to get user profile
            stateList.remove(state)
            url = "https://api.line.me/oauth2/v2.1/token"
            data = {
                "grant_type": "authorization_code",
                "Content-Type": "application/x-www-form-urlencoded",
                "code": code,
                "redirect_uri": config.call_back,
                "client_id": config.client_id,
                "client_secret": config.client_secret
            }
            res = requests.post(url=url, data=data)
            
            # Get user profile
            if res.status_code == 200:
                token = res.json()
                id_token = token["id_token"]
                id_url = "https://api.line.me/oauth2/v2.1/verify"
                id_data = {
                    "id_token": id_token,
                    "client_id": config.client_id
                }
                id_res = requests.post(url=id_url, data=id_data)
                id_res=id_res.json()
                print(id_res)
                hasMember=model.db.checkMemberExist(id_res["email"])
                if hasMember:
                    model.db.updateUserInfo(
                        id_res["name"], id_res["picture"], id_res["email"], token["access_token"])
                    result=member.ppTokenResponse(
                        hasMember["MemberID"], hasMember["Name"], (date.today()+timedelta(days=29)).isoformat(), token["access_token"])
                    return result
                else:
                    result=model.db.registerNewUser(id_res["name"],id_res["picture"],id_res["email"],token["access_token"])
                    if result:
                        hasMember = model.db.checkMemberExist(id_res["email"])
                        result = member.ppTokenResponse(
                            hasMember["MemberID"], hasMember["Name"], hasMember["TokenValidDate"], hasMember["LineToken"])
                        return result
                    else:
                        return jsonify({"error":True,"errormsg":"Cannot add new user, something wrong on database!"}), 500
            else:
                return jsonify({"error": True, "errormsg": "Token request fails!"})

        else:
            return jsonify({"error": True, "errormsg": "Wrong state code!"})
    
    def ppTokenResponse(MemberID, Name, Date, LineToken):
        PPToken = jwt.encode({
            'ID': MemberID,
            'Name': Name,
            'Date':Date,
            'LineToken':LineToken
            },
            config.PP_SECRET_KEY, algorithm=config.PP_JWT_ALGO)

        # Save to cookie
        res = make_response(
            redirect('/'))
        res.set_cookie('user', PPToken)
        print(res)
        return res
    
    def auth(token):
        if not token:
            return jsonify({"error":True,"errormsg":"Please log in."}), 200

        try:
            data = jwt.decode(token, config.PP_SECRET_KEY,
                              algorithms=config.PP_JWT_ALGO)
        except jwt.exceptions.InvalidTokenError as error:
            print(error)
            return jsonify({"error": True, "message": "Invalid token"}), 400
        today=date.today()
        if data["Date"]>today.isoformat():
            return jsonify({"data": {"id": data["ID"], "Name": data["Name"], "Date":data["Date"]}}), 200
        else:
            #Revoke user
            url = "https://api.line.me/oauth2/v2.1/revoke"
            payload={
                "Content-Type": "application/x-www-form-urlencoded",
                "cliden_id":config.client_id,
                "client_sectet":config.client_secret,
                "access_token":data["LineToken"]
            }
            requests.post(url=url, data=payload)
            return jsonify({"error":True, "errormsg":"Token expires, please log in again!"}), 400

    def logout(token):
        try:
            data = jwt.decode(token, config.PP_SECRET_KEY,
                              algorithms=config.PP_JWT_ALGO)
        except jwt.exceptions.InvalidTokenError as error:
            print(error)
            return jsonify({"error": True, "message": "Invalid token"}), 400
        # Revoke user
        url = "https://api.line.me/oauth2/v2.1/revoke"
        payload = {
            "Content-Type": "application/x-www-form-urlencoded",
            "cliden_id": config.client_id,
            "client_sectet": config.client_secret,
            "access_token": data["LineToken"]
        }
        requests.post(url=url, data=payload)
        res = make_response(jsonify({"ok": True, "msg":"User logs out successfully!"}), 200)
        res.delete_cookie('user')
        return res

    def member(token, Page):
        try:
            member = jwt.decode(token, config.PP_SECRET_KEY,
                              algorithms=config.PP_JWT_ALGO)
        except jwt.exceptions.InvalidTokenError as error:
            print(error)
            return jsonify({"error": True, "message": "Invalid token"}), 400
        result=model.db.GetMemberTrackingProduct(member["ID"],Page)
        if not result:
            result=model.db.getMemberInfoOnly(member['ID'])
            return jsonify({'result':result, 'TrackProduct':False}), 200
        
        return jsonify({'result':result, 'TrackProduct':True}),200
    
    def enableNotify(token, TrackingID, TargetPrice, ProdTitle):
        try:
            member = jwt.decode(token, config.PP_SECRET_KEY,
                                algorithms=config.PP_JWT_ALGO)
        except jwt.exceptions.InvalidTokenError as error:
            print(error)
            return jsonify({"error": True, "message": "Invalid token"}), 400
        
        result=model.db.setNotify(member["ID"], TrackingID, TargetPrice)
        if not result:
            return jsonify({"error":True}),500
        else:
            msg=f'Hi {member["Name"]},\n 已設定-{ProdTitle}-價格低於{TargetPrice}會通知您！'
            model.lineBot.sendmsg(token,msg)
            if model.db.checkTargetPrice(TargetPrice,TrackingID):
                msg = f'您追蹤的商品:{ProdTitle}\n 已經低於${TargetPrice}!'
                model.lineBot.sendmsg(token, msg)

        return jsonify({"ok":True}), 200
    
    def disableNotify(token,data):
        try:
            member = jwt.decode(token, config.PP_SECRET_KEY,
                                algorithms=config.PP_JWT_ALGO)
        except jwt.exceptions.InvalidTokenError as error:
            print(error)
            return jsonify({"error": True, "message": "Invalid token"}), 400
        
        result=model.db.cancelNotify(member['ID'],data['TrackingID'])
        if result:
            msg=f'Hi {member["Name"]}, 已取消-{data["ProdTitle"]}-到價通知。'
            model.lineBot.sendmsg(token,msg)
        return jsonify({"ok":True}),200


