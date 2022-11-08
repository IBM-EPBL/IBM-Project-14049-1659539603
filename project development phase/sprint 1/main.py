# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 20:00:13 2022

@author: ELCOT
"""

from flask import *
import re
from prettytable import from_db_cursor
import ibm_db
import ibm_db_dbi
app = Flask(__name__)

app.secret_key = 'a'
conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
con =ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'','')

def getLoginDetails():
    conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
    cur = conn.cursor()
    if 'email' not in session:
            loggedIn = False
            username = ''
            noOfItems = 0
    else:
            loggedIn = True
            cur.execute("SELECT userId, username FROM users WHERE email = ?", (session['email'], ))
            userId, username = cur.fetchone()
            cur.execute("SELECT count(productId) FROM kart WHERE userId = ?", (userId, ))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, username, noOfItems)

@app.route("/", methods=['GET', 'POST'])
def root():
    conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
    loggedIn, username, noOfItems = getLoginDetails()
    cur = conn.cursor()
    cur.execute('SELECT productId, name, price, description, image, stock FROM products')
    itemData = cur.fetchall()
    cur.execute('SELECT categoryId, name FROM categories')
    categoryData = cur.fetchall() 
    itemData = parse(itemData) 
    return render_template('home.html',itemData=itemData,categoryData=categoryData,loggedIn=loggedIn,username=username, noOfItems=noOfItems)



@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)
def is_valid(email, password):
   with conn as con:
      cur = con.cursor()
      cur.execute('SELECT email, password FROM users')
      data = cur.fetchall()
      for row in data:
        if row[0] == email and row[1] == password: 
            return True
   return False

@app.route("/productDescription")
def productDescription():
    conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
    loggedIn, username, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    cur = conn.cursor()
    cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ?', (productId, ))
    productData = cur.fetchone()
    conn.close() 
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, username = username, noOfItems = noOfItems)

@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'], ))
        userId = cur.fetchone()[0]
        try:
            cur.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
            conn.commit()
            msg = "Added successfully"
        except:
            conn.rollback()
            msg = "Error occured"
        conn.close()
        return redirect(url_for('root'))

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, username, noOfItems = getLoginDetails()
    email = session['email']
    conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
    cur = conn.cursor()
    cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
    userId = cur.fetchone()[0]
    cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
    products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, username=username, noOfItems=noOfItems)


        
@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

@app.route("/register", methods = ['GET', 'POST'])
def register():
     error = ''
     if request.method == 'POST':
         username = request.form['username']
         password = request.form['password']
         address = request.form['address']
         mobileNo = request.form['mobileNo']
         email = request.form['email']
         sql = "SELECT * FROM users WHERE username =?"
         stmt = ibm_db.prepare(con, sql)
         ibm_db.bind_param(stmt, 1, username)
         ibm_db.execute(stmt)
         account = ibm_db.fetch_assoc(stmt)
         print(account)
         if account:
             msg = 'Account already exists !'
         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
             msg = 'Invalid email address !'
         elif not re.match(r'[A-Za-z0-9]+', username):
             msg = 'name must contain only characters and numbers !'
         else:
           insert_sql = "INSERT INTO  users (username,password,address,mobileNO,email) VALUES (?, ?, ?, ?, ?)"
           prep_stmt = ibm_db.prepare(con, insert_sql)
           ibm_db.bind_param(prep_stmt, 1, username)
           ibm_db.bind_param(prep_stmt, 2, password)
           ibm_db.bind_param(prep_stmt, 3, address)
           ibm_db.bind_param(prep_stmt, 4, mobileNo)
           ibm_db.bind_param(prep_stmt, 5, email)
           ibm_db.execute(prep_stmt)
           error = 'You have successfully registered !'
     elif request.method == 'POST':
         error = 'Please fill out the form !'
     return render_template('register.html', error = error)
      
    
@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))


    


def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans
if __name__ == '__main__':
   app.run(host='0.0.0.0')
