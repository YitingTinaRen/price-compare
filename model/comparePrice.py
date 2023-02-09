import model
from flask import jsonify, make_response

class comparePrice:
    def searchCategory(CateLevel, CateName):
        print("in function comparPrice")
        print(f'CateLevel: {CateLevel}, CateName: {CateName}')
        result = db.SearchProductbyCategory(CateLevel, CateName)

        removeIndex = []
        for i in range(len(result)):
            # print(
            #     f"\n\nMomo Product Name: {result[i]['ProductName']},Momo Price: {result[i]['CurrentPrice']}")
            matchResult = db.ProductMatch(result[i]["ProductName"])
            if not matchResult:
                removeIndex.append(i)
            else:
                # print(
                #     f"PCHome ProductNick:{matchResult[0]['ProductNick']}, PCHome Price:{matchResult[0]['CurrentPrice']}, Matching score:{matchResult[0]['score']}")
                PCH = {
                    "PCHName": matchResult[0]['ProductName'],
                    "PCHNick": matchResult[0]['ProductNick'],
                    "PCHPrice": matchResult[0]["CurrentPrice"],
                    "PCHURL": matchResult[0]["ProductURL"]
                }
                result[i].update(PCH)

        for item in sorted(removeIndex, reverse=True):
            if item < len(result):
                del result[item]
        
        print(result)
        # return jsonify(result),200
        return result
    
    def getSearchResult(Category, Page):
        result = model.db.getResult(Category, Page)
        return jsonify(result),200
