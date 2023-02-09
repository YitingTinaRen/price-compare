from flask import *
import model

api_compare=Blueprint('api_compare',__name__)

@api_compare.route("/api/compare", methods=['GET'])
def compare():
    Category=request.args.get('Category')
    Page=request.args.get('Page',0)
    result = model.comparePrice.getSearchResult(Category, int(Page))
    return result