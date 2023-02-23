from flask import *
import model

api_compare=Blueprint('api_compare',__name__)

@api_compare.route("/api/compare", methods=['GET'])
def compare():
    Category=request.args.get('Category')
    Page=request.args.get('Page',0)
    Brand = request.args.get('Brand', '')
    if Brand:
        print("has brand")
        result = model.comparePrice.getSearchResult_brand(
            Category, 10*int(Page), Brand)
    else:
        result = model.comparePrice.getSearchResult(Category, 10*int(Page))
    
    return result


@api_compare.route("/api/brand", methods=['GET'])
def brand():
    Category = request.args.get('Category')
    result = model.comparePrice.getMomoBrands(Category)
    return result
