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
import ibm_boto3
from ibm_botocore.client import Config
from ibm_botocore.exceptions import ClientError
import ibm_s3transfer.manager

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

@app.route("/add")
def admin():
    conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
    cur = conn.cursor()
    cur.execute("SELECT categoryId, name FROM categories")
    categories = cur.fetchall()
    conn.close()
    return render_template('add.html', categories=categories)

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])
        new_bucket_name="menspants"
        #Uploading image procedure
        pics = request.files['image']
        new_item_name= name +".png"
        new_file_path=pics
        image="https://menspants.s3.jp-tok.cloud-object-storage.appdomain.cloud/"+name+".png"
        upload_large_file(new_bucket_name, new_item_name,new_file_path)
        try:
           conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
           cur = conn.cursor()
           insert_sql = "INSERT INTO  products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)"
           prep_stmt = ibm_db.prepare(con, insert_sql)
           ibm_db.bind_param(prep_stmt, 1, name)
           ibm_db.bind_param(prep_stmt, 2, price)
           ibm_db.bind_param(prep_stmt, 3, description)
           ibm_db.bind_param(prep_stmt, 4, image)
           ibm_db.bind_param(prep_stmt, 5, stock)
           ibm_db.bind_param(prep_stmt, 6, categoryId)
           ibm_db.execute(prep_stmt)
           msg="added successfully"
        except:
           msg="error occured"
           conn.rollback()
        conn.close() 
        print(msg)
        return redirect(url_for('root'))
    
@app.route("/remove")
def remove():
    conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
    cur = conn.cursor()
    cur.execute('SELECT productId, name, price, description, image, stock FROM products')
    data = cur.fetchall()
    conn.close()
    return render_template('remove.html', data=data)

@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
    try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = ?', (productId, ))
            conn.commit()
            msg = "Deleted successsfully"
    except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect(url_for('root'))

@app.route("/displayCategory")
def displayCategory():
        loggedIn, firstName, noOfItems = getLoginDetails()
        categoryId = request.args.get("categoryId")
        conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
        cur = conn.cursor()
        cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = ?", (categoryId, ))
        data = cur.fetchall()
        conn.close()
        categoryName = data[0][4]
        data = parse(data)
        return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryName=categoryName)

@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

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
   cur = conn.cursor()
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

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    conn = ibm_db_dbi.Connection(ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zlp37297;PWD=so1e9MAlFSDzhxfs",'',''))
    cur = conn.cursor()
    cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
    userId = cur.fetchone()[0]
    try:
            cur.execute("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
            conn.commit()
            msg = "removed successfully"
    except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('root'))

        
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


def log_done():
    print("DONE!\n")

def log_client_error(e):
    print("CLIENT ERROR: {0}\n".format(e))

def log_error(msg):
    print("UNKNOWN ERROR: {0}\n".format(msg))
    
def upload_large_file(bucket_name, item_name, file_path):
    print("Starting large file upload for {0} to bucket: {1}".format(item_name, bucket_name))

    # set the chunk size to 5 MB
    part_size = 1024 * 1024 * 5

    # set threadhold to 5 MB
    file_threshold = 1024 * 1024 * 5

    # set the transfer threshold and chunk size in config settings
    transfer_config = ibm_boto3.s3.transfer.TransferConfig(
        multipart_threshold=file_threshold,
        multipart_chunksize=part_size
    )

    # create transfer manager
    transfer_mgr = ibm_boto3.s3.transfer.TransferManager(cos_cli, config=transfer_config)

    try:
        # initiate file upload
        future = transfer_mgr.upload(file_path, bucket_name, item_name)

        # wait for upload to complete
        future.result()

        print ("Large file upload complete!")
    except Exception as e:
        print("Unable to complete large file upload: {0}".format(e))
    finally:
        transfer_mgr.shutdown()    
COS_ENDPOINT = "https://s3.jp-tok.cloud-object-storage.appdomain.cloud" # example: https://s3.us-south.cloud-object-storage.appdomain.cloud
COS_API_KEY_ID = "l3fM5rXs5ycS8W4SAclnSNJPsk6MMEVuExuEoeVJPJFW" # example: xxxd12V2QHXbjaM99G9tWyYDgF_0gYdlQ8aWALIQxXx4
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_SERVICE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/b9916d3d37d24674be1984ac2159a53c:da69c0d9-9adb-46b9-b72c-582469fca7ab::" # example: crn:v1:bluemix:public:cloud-object-storage:global:a/xx999cd94a0dda86fd8eff3191349999:9999b05b-x999-4917-xxxx-9d5b326a1111::
COS_STORAGE_CLASS = "us-south-smart" 

    # Create client connection
cos_cli = ibm_boto3.client("s3",
ibm_api_key_id=COS_API_KEY_ID,
ibm_service_instance_id=COS_SERVICE_CRN,
config=Config(signature_version="oauth"),
endpoint_url=COS_ENDPOINT
)


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
