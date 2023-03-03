import model
from flask import jsonify, make_response
import jwt
import config

class comparePrice:
    
    def getSearchResult(Category, Page, token):
        if token:
            try:
                member = jwt.decode(token, config.PP_SECRET_KEY,
                                    algorithms=config.PP_JWT_ALGO)
            except jwt.exceptions.InvalidTokenError as error:
                print(error)
                return jsonify({"error": True, "message": "Invalid token"}), 400
            result = model.db.getResult4Member(Category, Page, member['ID'])
            return jsonify(result), 200
        else:
            result = model.db.getResult(Category, Page)
            return jsonify(result),200

    def getMomoBrands(Category):
        result=model.db.getMomoBrand(Category)
        NameListLong = [sub['ProductName'] for sub in result]
        NameListShort = []
        for item in NameListLong:
            if item.find('】') == -1:
                    if item.find(' ') != -1:
                        NameListShort.append(item[:item.index(' ')])
            else:
                item = item.split('】')
                NameListShort.append(item[0].replace("【", ""))
        OutputList=list(set(NameListShort))
    
        return OutputList

    def getSearchResult_brand(Category, Page, Brand, token):
        if token:
            try:
                member = jwt.decode(token, config.PP_SECRET_KEY,
                                    algorithms=config.PP_JWT_ALGO)
            except jwt.exceptions.InvalidTokenError as error:
                print(error)
                return jsonify({"error": True, "message": "Invalid token"}), 400
            result = model.db.getResult_Brand4member(Category, Page, Brand,member['ID'])
            return jsonify(result), 200
        else:
            result = model.db.getResult_Brand(Category, Page, Brand)
            return jsonify(result), 200

    def getPriceHistory(momoID,PCHomeID):
        PCHomeHistory=model.db.getPCHPriceHistory(PCHomeID)
        MomoHistory=model.db.getMomoPriceHistory(momoID)
        print("PCHome")
        print(PCHomeHistory)
        print("Momo")
        print(MomoHistory)
        data={
            'PCHomeXLabels':[item['Date'] for item in PCHomeHistory],
            'PCHomeData':[item['Price'] for item in PCHomeHistory],
            'MomoXLabels':[item['Date'] for item in MomoHistory],
            'MomoData':[item['Price'] for item in MomoHistory]
        }
        print(data)
        return data
    
    def trackProduct(token, momoID, PCHID):
        try:
            member = jwt.decode(token, config.PP_SECRET_KEY,
                              algorithms=config.PP_JWT_ALGO)
        except jwt.exceptions.InvalidTokenError as error:
            print(error)
            return jsonify({"error": True, "message": "Invalid token"}), 400
        
        result=model.db.TrackProduct(member['ID'],momoID,PCHID,None,False)
        return jsonify(result), 200
    
    def unTrackProduct(token,MomoProdID, PCHProdID):
        try:
            member = jwt.decode(token, config.PP_SECRET_KEY,
                                algorithms=config.PP_JWT_ALGO)
        except jwt.exceptions.InvalidTokenError as error:
            print(error)
            return jsonify({"error": True, "message": "Invalid token"}), 400
        result = model.db.UnTrackProduct(MomoProdID, PCHProdID, member['ID'])
        return jsonify(result), 200

    def trackingRecord(token):
        try:
            member = jwt.decode(token, config.PP_SECRET_KEY,
                                algorithms=config.PP_JWT_ALGO)
        except jwt.exceptions.InvalidTokenError as error:
            print(error)
            return jsonify({"error": True, "message": "Invalid token"}), 400

        result = model.db.GetTrackingProduct(member['ID'])
        return jsonify(result), 200
