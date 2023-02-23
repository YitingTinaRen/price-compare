import model
from flask import jsonify, make_response

class comparePrice:
    
    def getSearchResult(Category, Page):
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

    def getSearchResult_brand(Category, Page, Brand):
        result = model.db.getResult_Brand(Category, Page, Brand)
        return jsonify(result), 200
