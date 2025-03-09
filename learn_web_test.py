from flask import Flask, render_template

app = Flask(__name__)

#创建了网址 /show/info 和 函数index 的对应关系
#以后用户在浏览器上访问 /show/info 网站自动执行 index
@app.route('/show/info')
def index():
    #return "中国联通"
    #Flask自动打开，读取并返回
    return render_template("index.html")


@app.route('/register')
def register():
    return render_template("register.html")

if __name__ == '__main__':
    app.run("register.html")