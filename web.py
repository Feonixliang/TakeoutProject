from flask import Flask, render_template

app = Flask(__name__)

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/system/rider')
def rider_system():
    return render_template("rider.html")
#顾客
@app.route('/system/customer')
def customer_system():
    return render_template("customer.html")
#merchant
@app.route('/system/merchant')
def merchant_system():
    return render_template("merchant.html")