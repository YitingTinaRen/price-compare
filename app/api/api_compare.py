from flask import *
import model

api_compare=Blueprint('api_compare',__name__)

@api_compare.route("/api/compare", methods=['GET'])
def compare():
    Category=request.args.get('Category')
    Page=request.args.get('page',0)
    Brand = request.args.get('Brand', '')
    token = request.cookies.get("user")
    if Brand:
        print("has brand")
        result = model.comparePrice.getSearchResult_brand(
            Category, 10*int(Page), Brand, token)
    else:
        result = model.comparePrice.getSearchResult(Category, 10*int(Page), token)
    
    return result


@api_compare.route("/api/brand", methods=['GET'])
def brand():
    Category = request.args.get('Category')
    result = model.comparePrice.getMomoBrands(Category)
    return result

@api_compare.route("/api/history", methods=["GET"])
def history():
    momoID=request.args.get('momoID')
    PCHomeID=request.args.get('PCHID') 
    result=model.comparePrice.getPriceHistory(momoID,PCHomeID)
    return result

@api_compare.route("/api/trackProduct", methods=["GET", "DELETE"])
def trackProduct():
    if request.method =="GET":
        token = request.cookies.get("user")
        momoID = request.args.get('momoID')
        PCHomeID = request.args.get('PCHID')
        result=model.comparePrice.trackProduct(token,momoID,PCHomeID)
        return result
    elif request.method =="DELETE":
        token = request.cookies.get("user")
        data = request.get_json()
        result=model.comparePrice.unTrackProduct(token, data['momoID'],data['PCHID'])
        return {"method":"delete"}
    

@api_compare.route("/api/trackingRecord", methods=["GET"])
def trackingRecord():
    token = request.cookies.get("user")
    result=model.comparePrice.trackingRecord(token)
    return result
