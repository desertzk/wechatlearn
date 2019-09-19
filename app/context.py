from flask import Flask,current_app
from flask_sqlalchemy import SQLAlchemy

# 常量
# 微信的token令牌
WECHAT_TOKEN = "zhangkai"
WECHAT_APPID = "wx2a2283f465f7f68a"
WECHAT_APPSECRET = "8c2e9217f7f608c2e040ba68cc788fab"



app = Flask(__name__,static_folder='../static', template_folder='../templates')


app.config.from_pyfile("../config/config.cfg")
# 要用session前需要设置密钥
app.config["SECRET_KEY"]="zzzzzzzzzzzzzzzzzkkkkkkkkkkkkkkkkkkkkkk"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://zk:zk@47.254.240.25:3306/medical'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
