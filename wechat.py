# coding:utf-8
import io
import pdb
import os.path
import random
import sys
import urllib.parse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#import http.client, urllib.parse
from flask import Flask, request, abort, render_template, redirect, flash, Response
import hashlib
import xmltodict
import time
# import urllib2
import json
import requests
import logging
from datetime import datetime
from urllib.parse import quote
from app.context import app,WECHAT_TOKEN,WECHAT_APPID,WECHAT_APPSECRET,db
from app.forms import RegisterForm,DailyCheckForm,WeightRecordForm,BloodPressureRecordForm,HeartRateRecordForm,LoginForm
from app.models import User,Daytimecheckdata
from app.drawimg import drawlinegraph,drawlinegraph2

import qrcode
import threading
import base64

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG

from matplotlib.figure import Figure




class wechatrequest():
    def __init__(self):
        self._wxaccesstoken=""
        checkthread = threading.Thread(target=self.checkupdatedbfile)
        checkthread.start()

    def checkupdatedbfile(self):
        while(True):
            time.sleep(3600)
            self.get_accesstoken()
            logging.info("timer get access_token :"+self._wxaccesstoken)

    def get_accesstoken(self):
        #if self._wxaccesstoken != "":
        #    return self._wxaccesstoken
        resp = requests.get(
            "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + WECHAT_APPID + "&secret=" + WECHAT_APPSECRET)
        if resp.status_code != 200:
            logging.info("request error"+resp.status_code)
            return ""
        retdict = json.loads(resp.text)
        self._wxaccesstoken = retdict["access_token"]
        return self._wxaccesstoken


    def wxgetuserinfo(self,open_id):
        url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" \
              % (self._wxaccesstoken, open_id)

        response = requests.get(url)
        response.encoding = 'utf-8'
        # data = response.json()
        # read wechat return json response data
        # pdb.set_trace()
        if response.status_code==200:
            return response.text

    # 客服接口-send message
    def sendwxmessagetouser(self,open_id,content):
        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" \
              % (self._wxaccesstoken)
        # logging.info(content)
        # logging.info(type(content))
        senddata='{  \
        "touser":"%s", \
        "msgtype":"text",   \
        "text":{"content":"%s"} \
        }'%(open_id,content)
        jsonsendstr=senddata.encode("utf-8")
        headers = {'Content-Type': 'application/json;encoding=utf-8'}
        response = requests.post(url,jsonsendstr,headers=headers)
        logging.info("post url"+url+"senddata:"+senddata+"response:"+response.text)

        jsondict=json.loads(response.text)
        if jsondict.get("errcode")==41001:
            logging.info(jsondict.get("errmsg"))
            self.get_accesstoken()
            response = requests.post(url, jsonsendstr,headers=headers)

    def send_tmp_media(self,filename):
        files = {'media': open(filename, 'rb')}
        url = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=image"% (self._wxaccesstoken)
        rsp = requests.post(url, files=files)
        logging.info(rsp.text)
        if self.checktoken(json.loads(rsp.text)):
            url = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=image"% (self._wxaccesstoken)
            rsp = requests.post(url, files=files)
            logging.info("get token and resend "+rsp.text)

        return rsp.text

    def checktoken(self,jsondict):
        if jsondict.get("errcode")==41001 or jsondict.get("errcode")==42001:
            logging.info(jsondict.get("errmsg"))
            self.get_accesstoken()
            return True
        else:
            return False
            #response = requests.post(url, jsonsendstr,headers=headers)




g_wxreq=wechatrequest()
g_wxreq.get_accesstoken()

@app.route("/wx", methods=["GET", "POST"])
def wechat():
    """对接微信公众号服务器"""
    # 接收微信服务器发送的参数
    #pdb.set_trace()
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    logging.info("signature"+signature)
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
        # logging.info("my sign:"+sign)
	    # logging.info("wechat sign:"+signature)
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
            print(xml_str)
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

            elif msg_type=="event":
                logging.info("event")
                if xml_dict.get("EventKey") == "my_medical_plan":
                    openid=xml_dict.get("FromUserName")
                    createqrcode(openid)
                    rspjson=g_wxreq.send_tmp_media("resources/"+openid+".jpg")
                    rspdict=json.loads(rspjson)
                    resp_dict = {
                        "xml": {
                            "ToUserName": xml_dict.get("FromUserName"),
                            "FromUserName": xml_dict.get("ToUserName"),
                            "CreateTime": int(time.time()),
                            "MsgType": "event",
                            "Event":"VIEW",
                            "EventKey":"www.qq.com"

                        }
                    }

                else:
                    openid=xml_dict.get("FromUserName")
                    createqrcode(openid)
                    rspjson=g_wxreq.send_tmp_media("resources/"+openid+".jpg")
                    rspdict=json.loads(rspjson)
                    logging.info("tmp media ok:"+rspjson)
                    resp_dict = {
                        "xml": {
                            "ToUserName": xml_dict.get("FromUserName"),
                            "FromUserName": xml_dict.get("ToUserName"),
                            "CreateTime": int(time.time()),
                            "MsgType": "image",
                            "Image":{
                                "MediaId":rspdict["media_id"]
                            }
                        }
                    }
            else:
                resp_dict = {
                    "xml": {
                        "ToUserName": xml_dict.get("FromUserName"),
                        "FromUserName": xml_dict.get("ToUserName"),
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": "thanks"
                    }
                }

            # 将字典转换为xml字符串
            resp_xml_str = xmltodict.unparse(resp_dict)
            logging.info("response value:"+resp_xml_str)
            # 返回消息数据给微信服务器
            return resp_xml_str



@app.route("/index")
def mainpage():
    open_id = request.args.get("open_id")
    return render_template('index.html',open_id=open_id)




@app.route("/index_for_doctor")
def index_for_doctor():
    open_id = request.args.get("open_id")

    return render_template('index_for_doctor.html',open_id=open_id)






@app.route("/sendtouserpage", methods=['GET', 'POST'])
def sendtouserpage():
    open_id=request.form.get("openid")
    pcontent=request.form.get("content")
    #pdb.set_trace()
    g_wxreq.sendwxmessagetouser(open_id,pcontent)
    return "success"

@app.route('/user/<identity_id>')
def show_user(identity_id):
    user = User.query.filter_by(identity_id=identity_id).first_or_404()
    # return render_template('show_user.html', user=user)
    return render_template('sendtouserpage.html', user=user)

@app.route("/usersmanagerment",methods=['GET'])
def query_all_users():
    identity_id = request.args.get("identity_id")
    login_user = User.query.filter_by(identity_id=identity_id).first()
    if login_user.role == 0 or login_user.role == 3:
        # userlist=User.query.order_by(User.name).all()
        doctorlist = User.query.filter_by(role=1)
        patientlist = User.query.filter_by(doctor_id=login_user.id)
        userlist =[x for x in doctorlist] + [x for x in patientlist]
    elif login_user.role == 1:
        userlist = User.query.filter_by(doctor_id=login_user.id)
    # elif login_user.role
    return render_template('usermanagerment.html', userlist=userlist)



@app.route("/after_register")
def after_register():
    return "注册成功"

@app.route("/registertest", methods=['GET', 'POST'])
def registertest():

    form = RegisterForm()
    return render_template('register.html', form=form,nkname="haha")


# userinfo page
@app.route("/getqrcode", methods=['GET'])
def getuserqrcode():
    # pdb.set_trace()
    openid = request.args.get('openid')
    logging.info("getuserqrcode:openid"+openid)
    user = User.query.filter_by(open_id=openid).first_or_404()
    daytimedatas=Daytimecheckdata.query.filter_by(identity_id=user.identity_id)
    # dates=[dayinfo.rhythm_of_heart for dayinfo in daytimedatas]

    dates=[]
    rhythm_of_hearts=[]
    for dayinfo in daytimedatas:
        dates.append(dayinfo.datetime)
        rhythm_of_hearts.append(dayinfo.rhythm_of_heart)

    output = drawlinegraph(dates,rhythm_of_hearts,"date","rhythm_of_heart")
    imgdata = "data:image/png;base64,"+base64.b64encode(output.getvalue()).decode("utf-8")

    return render_template('patientqrcode.html',user=user,daytimedatas=daytimedatas,num_x_points=50,imgdata=imgdata)


@app.route("/see")
def see():
    """ Returns html with the img tag for your plot.
    """
    num_x_points = int(request.args.get("num_x_points", 50))
    # in a real app you probably want to use a flask template.
    # return f"""
    # <h1>Flask and matplotlib</h1>
    # <h2>Random data with num_x_points={num_x_points}</h2>
    # <form method=get action="/">
    #   <input name="num_x_points" type=number value="{num_x_points}" />
    #   <input type=submit value="update graph">
    # </form>
    # <h3>Plot as a png</h3>
    # <img src="/matplot-as-image-{num_x_points}.png"
    #      alt="random points as png"
    #      height="200"
    # >
    # <h3>Plot as a SVG</h3>
    # <img src="/matplot-as-image-{num_x_points}.svg"
    #      alt="random points as svg"
    #      height="200"
    # >
    # """
    # from flask import render_template
    return render_template("image.html", num_x_points=num_x_points)


@app.route("/matplot-as-image-<string:open_id>.png")
def plot_newpng(open_id):
    """ renders the plot on the fly.
    """
    user = User.query.filter_by(open_id=open_id).first_or_404()
    daytimedatas=Daytimecheckdata.query.filter_by(identity_id=user.identity_id)
    # dates=[dayinfo.rhythm_of_heart for dayinfo in daytimedatas]
    dates=[]
    rhythm_of_hearts=[]
    for dayinfo in daytimedatas:
        dates.append(dayinfo.datetime)
        rhythm_of_hearts.append(dayinfo.rhythm_of_heart)

    output = drawlinegraph(dates,rhythm_of_hearts,"date","rhythm_of_heart")
    return Response(output.getvalue(), mimetype="image/png")


@app.route("/matplot-as-image-<int:num_x_points>.png")
def plot_png(num_x_points=50):
    """ renders the plot on the fly.
    """
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    x_points = range(num_x_points)
    axis.plot(x_points, [random.randint(1, 30) for x in x_points])

    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")


@app.route("/matplot-as-image-<int:num_x_points>.svg")
def plot_svg(num_x_points=50):
    """ renders the plot on the fly.
    """
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    x_points = range(num_x_points)
    axis.plot(x_points, [random.randint(1, 30) for x in x_points])

    output = io.BytesIO()
    FigureCanvasSVG(fig).print_svg(output)
    return Response(output.getvalue(), mimetype="image/svg+xml")

@app.route('/image')
def image():
    return render_template("image.html")



def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig





def createqrcode(open_id):
    url=app.config["HOST"]+"index_for_doctor?open_id="+open_id

    logging.info("createqrcodeurl:" + url)
    img = qrcode.make(url)
    img.save("resources/"+open_id+".jpg")
    return url


@app.route("/register", methods=['GET', 'POST'])
def register():
    # pdb.set_trace()
    form = RegisterForm()
    docters =db.session.query(User).filter((User.role==1)|(User.role==3)).all()
    form.doctor.choices = [ (item.id,item.name) for item in docters]
    logging.info(request.args)
    openid=request.args.get("wxopenid")
    identification=request.args.get("identification")
    email=request.args.get("email")
    doctor_id=int(request.args.get("doctor"))
    name=request.args.get("name")
    if openid !=None:
        try:
           userinfo=User.query.filter_by(identity_id=identification).first()
           if userinfo!=None:
               return "已经注册"

           user=User(name=name,identity_id=identification,open_id=openid,email=email,role=2,doctor_id=doctor_id)
           db.session.add(user)
           db.session.commit()
           return redirect('/after_register')
        except Exception as e:
            logging.info(e)
            return str(e)


    return render_template('register.html', form=form,nkname="")
    return "注册失败"




@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        logging.info("login"+form.identification.data)
        identity_id = form.identification.data
        password = form.password.data
        user = User.query.filter_by(identity_id=identity_id,password=password).first()
        if user==None:
            return render_template('login.html', form=form, nkname="身份证号或密码错误")
        else:
            return redirect('/usersmanagerment?identity_id='+user.identity_id)

    return render_template('login.html', form=form,nkname="医生登录")



@app.route("/registerpost", methods=['GET', 'POST'])
def registerpost():
    form = RegisterForm(doctor=0)

    if form.validate_on_submit():
        identity_id = form.identification.data
        user = User.query.filter_by(identity_id=identity_id).first()
        if user == None:
            logging.info(form.name.data+form.wxopenid.data)
            newuser=User(name=form.name.data,identity_id=form.identification.data,open_id=form.wxopenid.data,email=form.email.data,role=1,password=form.password.data)
            db.session.add(newuser)

        else:
            user.password=form.password.data

        db.session.commit()
        return redirect('/after_register')

    return render_template('register_docter.html', form=form,nkname="医生注册")







@app.route("/weight_info_doctor", methods=['GET'])
def weight_info_doctor():
    # pdb.set_trace()
    openid = request.args.get('open_id')
    logging.info("weight_info_doctor:open_id"+openid)
    user = User.query.filter_by(open_id=openid).first_or_404()
    daytimedatas=Daytimecheckdata.query.filter_by(identity_id=user.identity_id)
    # dates=[dayinfo.rhythm_of_heart for dayinfo in daytimedatas]

    dates=[]

    weights=[]
    for dayinfo in daytimedatas:
        if dayinfo.weight==None:
            continue
        dates.append(dayinfo.datetime)
        weights.append(dayinfo.weight)


    output = drawlinegraph(dates,weights,"date","weight")
    imgdata = "data:image/png;base64,"+base64.b64encode(output.getvalue()).decode("utf-8")

    return render_template('weight_info_doctor.html',user=user,daytimedatas=daytimedatas,imgdata=imgdata)




@app.route("/weight_info_record", methods=['GET', 'POST'])
def weight_info_record():

    openid = request.args.get('open_id')
    logging.info("in dailycheck openid="+openid)
    userinfo = User.query.filter_by(open_id=openid).first_or_404()
    form=request.form
    try:
        logging.info(form.get("weight"))
        daycheck = db.session.query(Daytimecheckdata).filter_by(identity_id=userinfo.identity_id,
                                                    datetime=datetime.today().strftime("%Y-%m-%d")).first()
        if daycheck!=None:
            daycheck.weight = form.get("weight")
        else:
            dailycheckdata = Daytimecheckdata(weight=form.get("weight"),identity_id=userinfo.identity_id,
                                             datetime=datetime.today().strftime("%Y-%m-%d"))
            db.session.add(dailycheckdata)


        db.session.commit()

        return render_template('index.html',open_id=openid)
    except Exception as ex:
        exstr = str(ex)

        logging.info(exstr)
        if "Duplicate entry" in exstr:
            return "不许重复录入"
        return str(ex)



@app.route("/weight_info", methods=['GET', 'POST'])
def weight_info():
    openid = request.args.get('open_id')
    print("in dailycheck openid="+openid)
    form = WeightRecordForm()

    return render_template('weight_info.html', form=form,open_id=openid)






@app.route("/blood_pressure_info", methods=['GET', 'POST'])
def blood_pressure_info():
    openid = request.args.get('open_id')
    logging.info("in dailycheck blood_pressure_info openid="+openid)
    form = BloodPressureRecordForm()

    return render_template('blood_pressure_info.html', form=form,open_id=openid)



@app.route("/blood_pressure_info_doctor", methods=['GET'])
def blood_pressure_info_doctor():
    # pdb.set_trace()
    openid = request.args.get('open_id')
    logging.info("blood_pressure_info_doctor:open_id"+openid)
    user = User.query.filter_by(open_id=openid).first_or_404()
    daytimedatas=Daytimecheckdata.query.filter_by(identity_id=user.identity_id)
    # dates=[dayinfo.rhythm_of_heart for dayinfo in daytimedatas]

    dates=[]
    diastolic_pressures=[]
    systolic_pressures=[]
    for dayinfo in daytimedatas:
        if dayinfo.diastolic_pressure==None or dayinfo.systolic_pressure==None:
            continue
        dates.append(dayinfo.datetime)
        diastolic_pressures.append(dayinfo.diastolic_pressure)
        systolic_pressures.append(dayinfo.systolic_pressure)

    output = drawlinegraph2(dates,diastolic_pressures,systolic_pressures,"date","blood_pressure")
    imgdata = "data:image/png;base64,"+base64.b64encode(output.getvalue()).decode("utf-8")

    return render_template('blood_pressure_info_doctor.html',user=user,daytimedatas=daytimedatas,imgdata=imgdata)




@app.route("/blood_pressure_record", methods=['GET', 'POST'])
def blood_pressure_record():
    openid = request.args.get('open_id')
    logging.info("in blood_pressure_record openid="+openid)
    userinfo = User.query.filter_by(open_id=openid).first_or_404()
    form=request.form
    try:

        daycheck = db.session.query(Daytimecheckdata).filter_by(identity_id=userinfo.identity_id,
                                                    datetime=datetime.today().strftime("%Y-%m-%d")).first()
        if daycheck!=None:
            daycheck.systolic_pressure = form.get("systolic_pressure")
            daycheck.diastolic_pressure = form.get("diastolic_pressure")
        else:
            dailycheckdata = Daytimecheckdata(systolic_pressure=form.get("systolic_pressure"),diastolic_pressure=form.get("diastolic_pressure"),identity_id=userinfo.identity_id,
                                             datetime=datetime.today().strftime("%Y-%m-%d"))
            db.session.add(dailycheckdata)


        db.session.commit()
        return render_template('index.html',open_id=openid)
    except Exception as ex:
        exstr = str(ex)

        logging.info(exstr)
        if "Duplicate entry" in exstr:
            return "不许重复录入"
        return str(ex)


@app.route("/heart_rate_record", methods=['GET', 'POST'])
def heart_rate_record():
    openid = request.args.get('open_id')
    logging.info("inheart_rate_record openid="+openid)
    userinfo = User.query.filter_by(open_id=openid).first_or_404()
    form=request.form
    try:

        daycheck = db.session.query(Daytimecheckdata).filter_by(identity_id=userinfo.identity_id,
                                                    datetime=datetime.today().strftime("%Y-%m-%d")).first()
        if daycheck!=None:
            daycheck.rhythm_of_heart = form.get("rhythm_of_heart")
        else:
            dailycheckdata = Daytimecheckdata(rhythm_of_heart=form.get("rhythm_of_heart"),identity_id=userinfo.identity_id,
                                             datetime=datetime.today().strftime("%Y-%m-%d"))
            db.session.add(dailycheckdata)


        db.session.commit()

        return render_template('index.html',open_id=openid)
    except Exception as ex:
        exstr = str(ex)

        print(exstr)
        if "Duplicate entry" in exstr:
            return "不许重复录入"
        return str(ex)



@app.route("/heart_rate_info_doctor", methods=['GET'])
def heart_rate_info_doctor():
    # pdb.set_trace()
    openid = request.args.get('open_id')
    logging.info("heart_rate_info_doctor:open_id"+openid)
    user = User.query.filter_by(open_id=openid).first_or_404()
    daytimedatas=Daytimecheckdata.query.filter_by(identity_id=user.identity_id)
    # dates=[dayinfo.rhythm_of_heart for dayinfo in daytimedatas]

    dates=[]
    rhythm_of_hearts=[]

    for dayinfo in daytimedatas:
        if dayinfo.rhythm_of_heart==None:
            continue
        dates.append(dayinfo.datetime)
        rhythm_of_hearts.append(dayinfo.rhythm_of_heart)


    output = drawlinegraph(dates,rhythm_of_hearts,"date","rhythm_of_heart")
    imgdata = "data:image/png;base64,"+base64.b64encode(output.getvalue()).decode("utf-8")

    return render_template('heart_rate_info_doctor.html',user=user,daytimedatas=daytimedatas,imgdata=imgdata)



@app.route("/heart_rate_info", methods=['GET', 'POST'])
def heart_rate_info():
    openid = request.args.get('open_id')
    print("in dailycheck openid="+openid)
    form = HeartRateRecordForm()

    return render_template('heart_rate_info.html', form=form,open_id=openid)






@app.route("/dailycheck", methods=['GET', 'POST'])
def dailycheck():
    openid = request.args.get('open_id')
    print("in dailycheck openid="+openid)
    form = DailyCheckForm()

    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.identification.data, form.diastolic_pressure.data))
        try:
            logging.info(form.identification.data)
            dailycheckdata=Daytimecheckdata(diastolic_pressure = form.diastolic_pressure.data
                                        ,systolic_pressure=form.systolic_pressure.data,
                                        identity_id=form.identification.data,
                                        rhythm_of_heart=form.rhythm_of_heart.data,
                                        #visit_time=form.visit_time.data,
                                        #triglyceride=form.triglyceride.data,
                                        #total_cholesterol=form.total_cholesterol.data,
                                        #hdl_c=form.hdl_c.data,
                                        #ldl_c=form.ldl_c.data,
                                        #BNP=form.BNP.data,
                                        #creatinine=form.creatinine.data,
                                        medicines_list=form.medicines_list.data)
            db.session.add(dailycheckdata)
            db.session.commit()

            return render_template('index.html',open_id=openid)
        except Exception as ex:
            exstr=str(ex)
            if "Duplicate entry" in exstr:
                return "不许重复录入"
            return str(ex)


    return render_template('dailycheck.html', form=form,nkname="haha")


#@app.route("/dailycheck", methods=['GET', 'POST'])
#def dailycheck():
#    form = DailyCheckForm()
#
#    if form.validate_on_submit():
#        flash('Login requested for user {}, remember_me={}'.format(
#            form.identification.data, form.diastolic_pressure.data))
#        try:
#            logging.info(form.identification.data)
#            dailycheckdata=Daytimecheckdata(diastolic_pressure = form.diastolic_pressure.data
#                                        ,systolic_pressure=form.systolic_pressure.data,
#                                        identity_id=form.identification.data,
#                                        rhythm_of_heart=form.rhythm_of_heart.data,
#                                        #visit_time=form.visit_time.data,
#                                        #triglyceride=form.triglyceride.data,
#                                        #total_cholesterol=form.total_cholesterol.data,
#                                        #hdl_c=form.hdl_c.data,
#                                        #ldl_c=form.ldl_c.data,
#                                        #BNP=form.BNP.data,
#                                        #creatinine=form.creatinine.data,
#                                        medicines_list=form.medicines_list.data)
#            db.session.add(dailycheckdata)
#            db.session.commit()
#
#            return "成功"
#        except Exception as ex:
#            exstr=str(ex)
#            if "Duplicate entry" in exstr:
#                return "不许重复录入"
#            return str(ex)
#
#
#    return render_template('patientqrcode.html', form=form,nkname="haha")




@app.route("/wx/index")
def index():
    """让用户通过微信访问的网页页面视图"""
    # 从微信服务器中拿去用户的资料数据
    # 1. 拿去code参数
    print(request.args)
    code = request.args.get("code")
    state = request.args.get("state")
    print("state:"+str(state))
    if not code:
        return u"缺失code参数"

    #logging.info("code:"+code)

    # 2. 向微信服务器发送http请求，获取access_token
    url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" \
          % (WECHAT_APPID, WECHAT_APPSECRET, code)
#http.client.HTTPConnection("192.168.73.21",9091)
    logging.info("in index:"+url)
    # 使用urllib2的urlopen方法发送请求
    # 如果只传网址url参数，则默认使用http的get请求方式, 返回响应对象
    response = requests.get(url)

    # 获取响应体数据,微信返回的json数据
    json_str = response.text
    resp_dict = json.loads(json_str)
    logging.info("json_str:"+json_str)
    # 提取access_token
    if "errcode" in resp_dict:
        return u"获取access_token失败"

    access_token = resp_dict.get("access_token")
    open_id = resp_dict.get("openid")  # 用户的编号
    logging.info("open_id"+open_id)

    if state=="2":
        print("already register")
        return render_template("index.html",open_id=open_id)
    else:
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
        logging.info("userinfo:"+user_json_str)
        if "errcode" in user_dict_data:
            return u"获取用户信息失败"+user_dict_data["errmsg"]
        else:
            # 将用户的资料数据填充到页面中
            #return render_template("index.html", user=user_dict_data)
            form = RegisterForm()
            doctors =db.session.query(User).filter((User.role==1)|(User.role==3)).all()
            form.doctor.choices = [ (item.id,item.name) for item in doctors]
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
    logging.info(usertokenresponse)

    # if usertokenresponse.status_code!=200:
    #     return

    jsdict = json.loads(usertokenresponse.text)
    access_tokenstr = jsdict["access_token"]

    userlistresponse = requests.get(
        'https://api.weixin.qq.com/cgi-bin/user/get?access_token=' + access_tokenstr)
    logging.info(userlistresponse)

    userinforesponse = requests.get(
        'https://api.weixin.qq.com/cgi-bin/user/info?access_token=' + access_tokenstr + '&openid=oCE0-wNsOEzivCjtXhIvA3iL2ieg&lang=zh_CN')
    pdb.set_trace()

    logging.info(userinforesponse.text)



#def runapp():
#    app.run(host="0.0.0.0",port=80, debug=True)


if __name__ == '__main__':
    #testinterface()
    #g_wxreq.send_tmp_media(r"H:\ccppworkspace\imageprocess\Project1\lena_top.jpg")
    infostr='{"openid":"oCE0-wNsOEzivCjtXhIvA3iL2ieg","nickname":"望尘莫及","sex":1,"language":"en","city":"杭州","province":"浙江","country":"中国","headimgurl":"http:\/\/thirdwx.qlogo.cn\/mmopen\/vi_32\/Q0j4TwGTfTKXzUU0bIPQWC6Xia07jenOIeoyEdNNyqEHMia1ZArFP01mXWB5DD2qzyIM3mwGy7IsiaK896icICRYuw\/132","privilege":[]}'
    FORMAT = '%(asctime)-15s %(message)s'
    ts = time.time()
    try:
        logging.basicConfig(format=FORMAT,filename='log/medicallog'+str(ts)+'.log',level=logging.INFO)

        app.run(host="0.0.0.0",port=8080, debug=True)
    except Exception as e:
        logging.exception(e)
