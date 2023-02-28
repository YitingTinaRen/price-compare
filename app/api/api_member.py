from flask import *
import model

api_member=Blueprint('api_member',__name__)

stateList=[]

@api_member.route("/api/login", methods=['GET'])
def login():
    result=model.member.login()
    return redirect(result)

@api_member.route("/api/callback", methods=['GET'])
def callback():
    code=request.args.get('code','')
    state = request.args.get('state','')
    error_desc = request.args.get('error_description', '')
    error_code = request.args.get('error', '')
    result=model.member.callback(code,state,error_desc,error_code)
    return result

@api_member.route("/api/auth", methods=["GET","DELETE"])
def auth():
    if request.method=="GET":
        token=request.cookies.get("user")
        result=model.member.auth(token)
        return result
    elif request.method=="DELETE":
        token = request.cookies.get("user")
        result=model.member.logout(token)
        return result

@api_member.route("/api/member", methods=["GET"])
def member():
    if request.method=="GET":
        token=request.cookies.get("user")
        Page=request.args.get('page',0)
        result=model.member.member(token,10*int(Page))
        return result