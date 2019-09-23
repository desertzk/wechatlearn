# coding:utf-8
import pdb
import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#import http.client, urllib.parse
from flask import Flask, request, abort, render_template,redirect,flash
import hashlib
import xmltodict
import time
# import urllib2
import json
import requests


from wechatlearn.app.context import app,WECHAT_TOKEN,WECHAT_APPID,WECHAT_APPSECRET,db
from wechatlearn.app.forms import RegisterForm
from wechatlearn.app.models import User






@app.route("/wx", methods=["GET", "POST"])
def wechat():
    """对接微信公众号服务器"""
    # 接收微信服务器发送的参数
    #pdb.set_trace()
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    print("signature"+signature)
#    pdb.set_trace()

    # 校验参数
    if not all([signature, timestamp, nonce]):
        abort(400)

    # 按照微信的流程进行计算签名
    li = [WECHAT_TOKEN, timestamp, nonce]
    # 排序
    li.sort()
    # 拼接字符串
    tmp_str = "".join(li)
    # 进行sha1加密, 得到正确的签名值
    sign = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()

    # 将自己计算的签名值与请求的签名参数进行对比，如果相同，则证明请求来自微信服务器
    if signature != sign:
        # 表示请求不是微信发的
        # print("my sign:"+sign)
	    # print("wechat sign:"+signature)
        abort(403)
    else:
        # 表示是微信发送的请求
        if request.method == "GET":
            # 表示是第一次接入微信服务器的验证
            echostr = request.args.get("echostr")
            if not echostr:
                abort(400)
            return echostr
        elif request.method == "POST":
            # 表示微信服务器转发消息过来
            xml_str = request.data
            if not xml_str:
                abort(400)

            # 对xml字符串进行解析
            xml_dict = xmltodict.parse(xml_str)
            xml_dict = xml_dict.get("xml")

            # 提取消息类型
            msg_type = xml_dict.get("MsgType")

            if msg_type == "text":
                # 表示发送的是文本消息
                # 构造返回值，经由微信服务器回复给用户的消息内容
                resp_dict = {
                    "xml": {
                        "ToUserName": xml_dict.get("FromUserName"),
                        "FromUserName": xml_dict.get("ToUserName"),
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": xml_dict.get("Content")
                    }
                }
            else:
                resp_dict = {
                    "xml": {
                        "ToUserName": xml_dict.get("FromUserName"),
                        "FromUserName": xml_dict.get("ToUserName"),
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": "i love u"
                    }
                }

            # 将字典转换为xml字符串
            resp_xml_str = xmltodict.unparse(resp_dict)
            # 返回消息数据给微信服务器
            return resp_xml_str



@app.route("/")
def mainpage():
    return render_template('index.html')



@app.route('/user/<identity_id>')
def show_user(identity_id):
    user = User.query.filter_by(identity_id=identity_id).first_or_404()
    # return render_template('show_user.html', user=user)
    return user.name+user.open_id+user.email

@app.route("/usersmanagerment")
def query_all_users():
    userlist=User.query.order_by(User.name).all()
    return render_template('usermanagerment.html', userlist=userlist)



@app.route("/after_register")
def after_register():
    return "注册成功"

@app.route("/registertest", methods=['GET', 'POST'])
def registertest():

    form = RegisterForm()
    return render_template('register.html', form=form,nkname="haha")



@app.route("/register", methods=['GET', 'POST'])
def register():
    # pdb.set_trace()
    form = RegisterForm()
    print(request.args)
    openid=request.args.get("wxopenid")
    identification=request.args.get("identification")
    email=request.args.get("email")

    name=request.args.get("name")
    if openid !=None:
        try:
           userinfo=User.query.filter_by(username='admin').first()
           if userinfo!=None:
               return "已经注册"

           user=User(name=name,identity_id=identification,open_id=openid,email=email)
           db.session.add(user)
           db.session.commit()
           return redirect('/after_register')
        except Exception as e:
            print(e)
            return str(e)


    return render_template('register.html', form=form,nkname="haha")
    return "注册失败"



@app.route("/registerpost", methods=['GET', 'POST'])
def registerpost():
    form = RegisterForm()

    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.name.data, form.wxopenid.data))
        print(form.name.data+form.wxopenid.data)
        user=User(name=form.name.data,identity_id=form.identification.data,open_id=form.wxopenid.data,email=form.email.data)
        db.session.add(user)
        db.session.commit()
        return redirect('/after_register')

    return render_template('register.html', form=form,nkname="haha")



@app.route("/wx/index")
def index():
    """让用户通过微信访问的网页页面视图"""
    # 从微信服务器中拿去用户的资料数据
    # 1. 拿去code参数
    code = request.args.get("code")

    if not code:
        return u"确实code参数"

    #print("code:"+code)

    # 2. 向微信服务器发送http请求，获取access_token
    url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" \
          % (WECHAT_APPID, WECHAT_APPSECRET, code)
#http.client.HTTPConnection("192.168.73.21",9091)

    #print("in index:"+url)
    # 使用urllib2的urlopen方法发送请求
    # 如果只传网址url参数，则默认使用http的get请求方式, 返回响应对象
    response = requests.get(url)

    # 获取响应体数据,微信返回的json数据
    json_str = response.text
    resp_dict = json.loads(json_str)
    print("json_str:"+json_str)
    # 提取access_token
    if "errcode" in resp_dict:
        return u"获取access_token失败"

    access_token = resp_dict.get("access_token")
    open_id = resp_dict.get("openid")  # 用户的编号
    print("open_id"+open_id)
    # 3. 向微信服务器发送http请求，获取用户的资料数据
    url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" \
          % (access_token, open_id)

    response = requests.get(url)
    response.encoding = 'utf-8'
    #data = response.json()
    # 读取微信传回的json的响应体数据
    #pdb.set_trace()
    user_json_str = response.text
    user_dict_data = json.loads(user_json_str)
    print("userinfo:"+user_json_str)
    if "errcode" in user_dict_data:
        return u"获取用户信息失败"+user_dict_data["errmsg"]
    else:
        # 将用户的资料数据填充到页面中
        #return render_template("index.html", user=user_dict_data)
        form = RegisterForm()
        form.wxopenid.data=open_id
        form.json_user_info=user_json_str
        form.sex.data=user_dict_data["sex"]
        return render_template('register.html', form=form,nkname=user_json_str)



def get_accesstoken():
    resp = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + WECHAT_APPID + "&secret=" + WECHAT_APPSECRET)
    if resp.status_code!=200:
        return
    retdict = json.loads(resp.text)
    access_token = retdict["access_token"]


def testinterface():
    usertokenresponse = requests.get(
        'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx2a2283f465f7f68a&secret=8c2e9217f7f608c2e040ba68cc788fab',
        auth=('user', 'pass'))
    print(usertokenresponse)

    # if usertokenresponse.status_code!=200:
    #     return

    jsdict = json.loads(usertokenresponse.text)
    access_tokenstr = jsdict["access_token"]

    userlistresponse = requests.get(
        'https://api.weixin.qq.com/cgi-bin/user/get?access_token=' + access_tokenstr)
    print(userlistresponse)
    
    userinforesponse = requests.get(
        'https://api.weixin.qq.com/cgi-bin/user/info?access_token=' + access_tokenstr + '&openid=oCE0-wNsOEzivCjtXhIvA3iL2ieg&lang=zh_CN')
    pdb.set_trace()

    print(userinforesponse.text)




if __name__ == '__main__':
    #testinterface()

    infostr='{"openid":"oCE0-wNsOEzivCjtXhIvA3iL2ieg","nickname":"望尘莫及","sex":1,"language":"en","city":"杭州","province":"浙江","country":"中国","headimgurl":"http:\/\/thirdwx.qlogo.cn\/mmopen\/vi_32\/Q0j4TwGTfTKXzUU0bIPQWC6Xia07jenOIeoyEdNNyqEHMia1ZArFP01mXWB5DD2qzyIM3mwGy7IsiaK896icICRYuw\/132","privilege":[]}'

    app.run(host="0.0.0.0",port=80, debug=True)
