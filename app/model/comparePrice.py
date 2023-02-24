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

    def getPriceHistory(momoID,PCHomeID):
        PCHomeHistory=model.db.getPCHPriceHistory(PCHomeID)
        MomoHistory=model.db.getMomoPriceHistory(momoID)
        data={
            'PCHomeXLabels':[item['Date'] for item in PCHomeHistory],
            'PCHomeData':[item['Price'] for item in PCHomeHistory],
            'MomoXLabels':[item['Date'] for item in MomoHistory],
            'MomoData':[item['Price'] for item in MomoHistory]
        }
        return data
