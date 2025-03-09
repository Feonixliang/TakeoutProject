from flask import Flask, render_template

app = Flask(__name__)

#创建了网址 /show/info 和 函数index 的对应关系
#以后用户在浏览器上访问 /show/info 网站自动执行 index
@app.route('/show/info')
def index():
    #return "中国联通"
    #Flask自动打开，读取并返回
    return render_template("index.html")

@app.route('/get/waimai')
def get_news():
    return render_template("首页.html")

#骑手
@app.route('/get/riderSystem')
def get_rider_system():
    return render_template("rider.html")
#顾客
@app.route('/get/customerSystem')
def get_customer_system():
    return render_template("customer.html")
#merchant
@app.route('/get/merchantSystem')
def get_merchant_system():
    return render_template("merchant.html")


if __name__ == '__main__':
    app.run()