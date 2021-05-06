"""
Final project
By: Nick Menough

"""
from flask import g, flash, Flask, jsonify, redirect, render_template, request, session
# from flask_sqlalchemy import SQLAlchemy# attempting SQL Alchemy 03/24/21
from sqlalchemy import create_engine, MetaData, Table
# import sqlite3 #removed raw sqlite 3/27/21
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEBUG"] = True
app.config["TESTING"] = True
app.config["SECRET_KEY"] = "baberuth"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False

THIS_PATH = os.path.dirname(os.path.abspath(__file__))
DATABASE = "sqlite:///" + os.path.join(THIS_PATH, "data/my_pantry.db")
print(DATABASE)
db = create_engine(DATABASE, convert_unicode=True)
metadata = MetaData(bind=db)
# db=SQLAlchemy.create_engine("sqlite:///"+DATABASE)# attempting SQL Alchemy 03/24/21
# app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///"+DATABASE
# db=SQLAlchemy(app)


""" removed raw sqlite3 4/29/21 this didnt work 
def make_dicts(cur,row):
    # convert the results of the query to a python dictionary
    return dict((cur.description[idx][0],value) for idx,value in enumerate(row))

def get_db():
    #function to retrieve the active Database
    db=getattr(g,"_database",None)
    if db==None:
        db=g._database=sqlite3.connect(DATABASE)
        db.row_factory=make_dicts
    return db

def query_db(query, args=(),one=False):
    #query database using sql query
    #if app.config["DEBUG"]:
    print(query,args)
    c=get_db().execute(query,args)
    results=c.fetchall()
    #if app.config["DEBUG"]:
    print(len(results),"results")
    c.close()
    return (results[0] if results else None) if one else results

@app.teardown_appcontext
def close_db(exception):
    #close the database when the application closes
    db=get_db()
    if db is not None:
        db.close()
"""


def login_required(f):
    @wraps(f)
    def dec_funct(*args, **kwargs):
        if "userID" not in session:
            flash('You must be logged in to view this page content!', 'danger')
            return redirect("/login")
        return f(*args, **kwargs)

    return dec_funct


def query_dict(query, **args):
    # query database using sql query
    # if app.config["DEBUG"]:
    try:
        print(query, args)
        if len(args) > 0:
            results = db.execute(query, args)
        else:
            results = db.execute(query)
        if results:
            results = [dict(row) for row in results]
            # if app.config["DEBUG"]:
            print(results)
    except:
        print("ERROR: Query failed!")
        return None
    return results


@app.route("/setup")
def setup():
    """ Creates the starting database"""
    password = generate_password_hash("password")
    # query=f"insert into login('username','password') values('admin','{password}')"
    # results=query_db(query,one=True)
    # results=db.engine.execute(query)# attempting SQL Alchemy 03/24/21

    # Clear all tables
    try:
        query = "delete from login where true;"
        db.execute(query)
        query = "delete from account where true;"
        db.execute(query)
    except:
        flash('Unable to clear existing database data.', 'danger')
        return redirect("/")

    try:
        query = "insert into login(username, password) values('admin',:password);"
        db.execute(query, password=password)
        query = "select userID from login where username='admin'"
        results = query_dict(query)
        query = "insert into account(userid, name, email) values(:userid, 'Admin', 'admin@mypantryy.com');"
        db.execute(query, userid=results[0]["userID"])
    except:
        flash('Unable to create starting database data.', 'danger')
        return redirect("/")
    flash('Database has been reset', 'success')
    return redirect("/")


@app.route('/')
def index():
    print(session)
    return render_template("index.html", session=session)


@app.route('/contact')
def contact():
    print(session)
    return render_template("contact.html", session=session)


@app.route('/myaccount',methods=["GET","POST"])
@login_required
def myaccount():
    if request.method=="POST":
        password = ""
        confirm = ""

        if request.form.get("password"):
            password = request.form.get("password")
        else:
            flash('Invalid or missing password', 'danger')
            return redirect("/myaccount")
        if request.form.get("confirm") and request.form.get("confirm") == password:
            confirm = request.form.get("confirm")
        else:
            flash('Invalid or missing confirmation password', 'danger')
            return redirect("/myaccount")

        hashpass = generate_password_hash(password)
        # query=f"insert into login ('username','password') values('{username}','{hashpass}');"
        # results=query_db(query,one=True)
        query = "update login set password=:hashpass where userID=:user_id;"
        try:
            db.execute(query, hashpass=hashpass,user_id=session["userID"])

        except:
            flash('Update password failed!', 'danger')
            return redirect("/myaccount")
        flash('Password updated!', 'success')
    query = "select * from login left join account on login.userID=account.userid where login.userID=:user_id;"
    results = query_dict(query, user_id=session["userID"])
    if results is None or len(results) < 1:
        flash('User ID does not exist!', 'danger')
        return redirect("/login")
    return render_template("myaccount.html", session=session,user=results[0])

## resetting password
@app.route('/passreset',methods=["GET","POST"])
def passreset():
    if request.method=="GET":
        return render_template("passreset.html")
    if request.method=="POST":
        username=""
        password = ""
        confirm = ""
        sec_a1=""
        sec_a2=""
        if request.form.get("username"):
            username = request.form.get("username").lower().strip()
        else:
            flash('Invalid or missing username', 'danger')
            return redirect("/passreset")
        if request.form.get("password"):
            password = request.form.get("password")
        else:
            flash('Invalid or missing password', 'danger')
            return redirect("/passreset")
        if request.form.get("confirm") and request.form.get("confirm") == password:
            confirm = request.form.get("confirm")
        else:
            flash('Invalid or missing confirmation password', 'danger')
            return redirect("/passreset")
        if request.form.get("sec-a1"):
            sec_a1 = request.form.get("sec-a1").lower().strip()
        else:
            flash('Missing Security answer #1!', 'danger')
            return redirect("/passreset")
        if request.form.get("sec-a2"):
            sec_a2 = request.form.get("sec-a2").lower().strip()
        else:
            flash('Missing Security answer #2!', 'danger')
            return redirect("/passreset")
        hashpass = generate_password_hash(password)
        query="select * from login left join account on login.userID=account.userid " + \
            "where username = :username;"
        results=query_dict(query,username=username)
        if results is None or len(results)<1:
            flash('Invalid username!', 'danger')
            return redirect("/passreset")
        if results[0]["sec_a1"].lower()!=sec_a1.lower() or results[0]["sec_a2"].lower()!=sec_a2.lower():
            flash('Security answers do not match!', 'danger')
            print(results[0]["sec_a1"].lower(),sec_a1.lower() or results[0]["sec_a2"].lower(),sec_a2.lower())
            return redirect("/passreset")


        query = "update login set password=:hashpass where username=:username;"
        try:
            db.execute(query, hashpass=hashpass,username=username)

        except:
            flash('Update password failed!', 'danger')
            return redirect("/passreset")
        flash('Password updated!', 'success')
        return redirect("/login")

@app.route('/get_questions',methods=["POST"])
def get_questions():
    username=""
    if request.form.get("username"):
        username = request.form.get("username").lower().strip()
    else:
        return jsonify({})
    query = "select username,sec_q1,sec_q2 from login left join account on login.userID=account.userid " + \
            "where login.username=:username;"
    results = query_dict(query, username=username)
    if results is None or len(results) < 1:
         return jsonify({})
    return jsonify(results[0])
""" 
current route method is to get the querie for the current page. added 5/2/2021

"""
@app.route('/current', methods=["GET", "POST"])
@login_required
def current():
    # query grand total on the current page.
    query = "select sum(qty) as qty,sum(price*qty) as total from category left join " + \
            "(select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item " + \
            "left join products on products.id=inventory_item.product_id where inventory_item.user_id=:user_id and is_custom=0 union " + \
            "select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item " + \
            "left join customer_products on customer_products.id=inventory_item.product_id where inventory_item.user_id=:user_id and is_custom=1) as all_products " + \
            "on category.id=all_products.cat_id;"
    totals = query_dict(query, user_id=session["userID"])[0]
    # query category sum and total per category
    query = "select category.id,category.name,sum(qty) as qty,sum(price*qty) as total from category left join " + \
            "(select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item " + \
            "left join products on products.id=inventory_item.product_id where inventory_item.user_id=:user_id and is_custom=0 union " + \
            "select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item " + \
            "left join customer_products on customer_products.id=inventory_item.product_id where inventory_item.user_id=:user_id and is_custom=1) as all_products " + \
            "on category.id=all_products.cat_id group by category.id;"
    categories = query_dict(query, user_id=session["userID"])
    query = "select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item left join " + \
            "products on products.id=inventory_item.product_id " + \
            "where inventory_item.user_id=:user_id and is_custom=0 union " + \
            "select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item left join " + \
            "customer_products on customer_products.id=inventory_item.product_id " + \
            "where inventory_item.user_id=:user_id and is_custom=1 " + \
            "order by name ;"
    products = query_dict(query, user_id=session["userID"])
    # the get page request
    if request.method == "GET":

        if not products:
            flash('No products found inventory', "info")
        return render_template("current.html", session=session, categories=categories, products=products, totals=totals)
    # form post route
    else:
        id = ""
        qty = 0
        price = 0
        exp_date = ""
        if request.form.get("id"):
            id = request.form.get("id")
        else:
            flash('Invalid or missing product id', 'danger')
            return render_template("current.html", session=session, categories=categories, products=products,
                                   totals=totals)
        if request.form.get("qty"):
            qty = int(request.form.get("qty"))
        else:
            flash('Invalid or missing quantity', 'danger')
            return render_template("current.html", session=session, categories=categories, products=products,
                                   totals=totals)
        if request.form.get("cost"):
            price = float(request.form.get("cost"))
        else:
            flash('Invalid or missing product cost', 'danger')
            return render_template("current.html", session=session, categories=categories, products=products,
                                   totals=totals)
        if request.form.get("exp"):
            exp_date = request.form.get("exp")
        else:
            flash('Invalid or missing expiration date', 'danger')
            return render_template("current.html", session=session, categories=categories, products=products,
                                   totals=totals)
        if qty > 0:

            query = "update inventory_item set qty=:qty ,price=:price,exp_date=:exp_date " + \
                    "where id=:id;"
        else:
            query = "delete from inventory_item where id=:id";

        try:
            db.execute(query, id=id, qty=qty, price=price, exp_date=exp_date)
            flash('Updated item', 'success')

        except:
            flash('Unable to update item', 'danger')
            return render_template("current.html", session=session, categories=categories, products=products,
                                   totals=totals)
        query = "select sum(qty) as qty,sum(price*qty) as total from category left join " + \
                "(select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item " + \
                "left join products on products.id=inventory_item.product_id where inventory_item.user_id=:user_id and is_custom=0 union " + \
                "select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item " + \
                "left join customer_products on customer_products.id=inventory_item.product_id where inventory_item.user_id=:user_id and is_custom=1) as all_products " + \
                "on category.id=all_products.cat_id;"
        totals = query_dict(query, user_id=session["userID"])[0]
        # query category sum and total per category
        query = "select category.id,category.name,sum(qty) as qty,sum(price*qty) as total from category left join " + \
                "(select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item " + \
                "left join products on products.id=inventory_item.product_id where inventory_item.user_id=:user_id and is_custom=0 union " + \
                "select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item " + \
                "left join customer_products on customer_products.id=inventory_item.product_id where inventory_item.user_id=:user_id and is_custom=1) as all_products " + \
                "on category.id=all_products.cat_id group by category.id;"
        categories = query_dict(query, user_id=session["userID"])
        query = "select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item left join " + \
                "products on products.id=inventory_item.product_id " + \
                "where inventory_item.user_id=:user_id and is_custom=0 union " + \
                "select inventory_item.id, cat_id, name, qty, exp_date, price from inventory_item left join " + \
                "customer_products on customer_products.id=inventory_item.product_id " + \
                "where inventory_item.user_id=:user_id and is_custom=1 " + \
                "order by name ;"
        products = query_dict(query, user_id=session["userID"])

        if not products:
            flash('No products found inventory', "info")
        return render_template("current.html", session=session, categories=categories, products=products, totals=totals)


@app.route('/update', methods=["GET", "POST"])
@login_required
def update():
    query = "select * from category;"
    categories = query_dict(query)
    if request.method == "GET":
        return render_template("update.html", session=session, categories=categories)
    else:
        product_id = ""
        qty = 0
        price = 0
        exp_date = ""
        is_custom = 0
        if request.form.get("id"):
            product_id = request.form.get("id")
        else:
            flash('Invalid or missing product id', 'danger')
            return render_template("update.html", session=session, categories=categories)
        if request.form.get("qty"):
            qty = int(request.form.get("qty"))
        else:
            flash('Invalid or missing quantity', 'danger')
            return render_template("update.html", session=session, categories=categories)
        if request.form.get("cost"):
            price = float(request.form.get("cost"))
        else:
            flash('Invalid or missing product cost', 'danger')
            return render_template("update.html", session=session, categories=categories)
        if request.form.get("exp"):
            exp_date = request.form.get("exp")
        else:
            flash('Invalid or missing expiration date', 'danger')
            return render_template("update.html", session=session, categories=categories)
        if request.form.get("user_id"):
            is_custom = 1
        query = "insert into inventory_item(product_id,user_id,qty,price,exp_date,is_custom) " + \
                "values(:product_id,:user_id,:qty,:price,:exp_date,:is_custom);"
        try:
            db.execute(query, product_id=product_id, user_id=session["userID"], qty=qty, price=price,
                       exp_date=exp_date, is_custom=is_custom)
        except:
            flash('Unable to add item to database', 'danger')
            return render_template("update.html", session=session, categories=categories)
        flash('Item added to your current inventory', 'success')
        return render_template("update.html", session=session, categories=categories)


@app.route('/add_new', methods=["POST"])
@login_required
def add_new():
    name = ""
    category = 0
    qty = 0
    price = 0
    exp_date = ""
    is_custom = 1
    if request.form.get("name"):
        name = request.form.get("name")
    else:
        flash('Invalid or missing name', 'danger')
        return redirect("/update")
    if request.form.get("category"):
        category = int(request.form.get("category"))
    else:
        flash('Invalid or missing category', 'danger')
        return redirect("/update")
    if request.form.get("qty"):
        qty = int(request.form.get("qty"))
    else:
        flash('Invalid or missing quantity', 'danger')
        return redirect("/update")
    if request.form.get("cost"):
        price = float(request.form.get("cost"))
    else:
        flash('Invalid or missing product cost', 'danger')
        return redirect("/update")
    if request.form.get("exp"):
        exp_date = request.form.get("exp")
    else:
        flash('Invalid or missing expiration date', 'danger')
        return redirect("/update")
    query = "insert into customer_products(user_id,name,cat_id) " + \
            "values(:user_id,:name,:cat_id);"
    try:
        print(query, session["userID"], name, category)
        db.execute(query, user_id=session["userID"], name=name, cat_id=category)
    except:
        flash('Unable to add custom item to database', 'danger')
        return redirect("/update")
    query = "select id from customer_products where user_id=:user_id and name=:name;"
    results = query_dict(query, user_id=session["userID"], name=name)
    if results is None or len(results) < 1:
        flash('Something unexpected happened', 'danger')
        return redirect("/update")

    query = "insert into inventory_item(product_id,user_id,qty,price,exp_date,is_custom) " + \
            "values(:product_id,:user_id,:qty,:price,:exp_date,:is_custom);"
    try:
        print(query, results[0]["id"], session["userID"], qty, price,
              exp_date, is_custom)
        db.execute(query, product_id=results[0]["id"], user_id=session["userID"], qty=qty, price=price,
                   exp_date=exp_date, is_custom=is_custom)
    except:
        flash('Unable to add item to database', 'danger')
        return redirect("/update")
    flash('Item added to your current inventory', 'success')
    return redirect("/update")


@app.route('/logout')
@login_required
def logout():
    session.clear()
    print(session)
    return redirect('/')


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handles the login request.
       if a get request display login page.
       if a post request attempt to login a user"""
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        if "userID" in session:
            flash('Login canceled, you were already logged in!', 'warning')
            return redirect("/")
        username = ""
        password = ""
        if request.form.get("username"):
            username = request.form.get("username").lower().strip()
        if request.form.get("password"):
            password = request.form.get("password")
        # results=db.engine.execute(query) # attempting SQL Alchemy 03/24/21
        # query=f"select * from login where username='{username}';"
        # results=query_db(query,one=True)
        query = "select * from login where username=:username;"
        results = query_dict(query, username=username)
        if results is not None and len(results) > 0 and check_password_hash(results[0]["password"], password):
            session["userID"] = results[0]["userID"]
            session["username"] = results[0]["username"]
            query = "select name, email from account where userid=:userid"
            results = query_dict(query, userid=results[0]["userID"])
            if len(results) > 0:
                session["name"] = results[0]["name"]
                session["email"] = results[0]["email"]
            flash('Congrats! You are logged in.', 'success')
            return redirect("/")
        else:
            flash('Invalid username or password!', 'danger')
            return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    """Handles the register request.
       if a get request display register page.
       if a post request attempt to register a user"""
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = ""
        password = ""
        confirm = ""
        name = ""
        email = ""
        sec_q1=""
        sec_q2=""
        sec_a1=""
        sec_a2=""
        if request.form.get("username"):
            username = request.form.get("username").lower().strip()
        else:
            flash('Invalid or missing username', 'danger')
            return render_template("register.html")
        if request.form.get("password"):
            password = request.form.get("password")
        else:
            flash('Invalid or missing password', 'danger')
            return render_template("register.html")
        if request.form.get("confirm") and request.form.get("confirm") == password:
            confirm = request.form.get("confirm")
        else:
            flash('Invalid or missing confirmation password', 'danger')
            return render_template("register.html")
        if request.form.get("name"):
            name = request.form.get("name")
        else:
            flash('Invalid or missing name', 'danger')
            return render_template("register.html")
        if request.form.get("email"):
            email = request.form.get("email").lower().strip()
        else:
            flash('Invalid or missing email', 'danger')
            return render_template("register.html")
        if request.form.get("sec-q1"):
            sec_q1 = request.form.get("sec-q1")
        else:
            flash('Missing Security Question #1!', 'danger')
            return render_template("register.html")
        if request.form.get("sec-q2"):
            sec_q2 = request.form.get("sec-q2")
        else:
            flash('Missing Security Question #2!', 'danger')
            return render_template("register.html")
        if request.form.get("sec-a1"):
            sec_a1 = request.form.get("sec-a1").lower().strip()
        else:
            flash('Missing Security answer #1!', 'danger')
            return render_template("register.html")
        if request.form.get("sec-a2"):
            sec_a2 = request.form.get("sec-a2").lower().strip()
        else:
            flash('Missing Security answer #2!', 'danger')
            return render_template("register.html")
        hashpass = generate_password_hash(password)
        # query=f"insert into login ('username','password') values('{username}','{hashpass}');"
        # results=query_db(query,one=True)
        query = "insert into login ('username','password') values(:username, :hashpass);"
        try:
            db.execute(query, username=username, hashpass=hashpass)
            query = "select userID from login where username=:username"
        except:
            flash('Username already taken', 'danger')
            return render_template("register.html")
        try:
            results = query_dict(query, username=username)
            query = "insert into account(userid, name, email,sec_q1,sec_q2,sec_a1,sec_a2) " + \
                    "values(:userid, :name, :email, :sec_q1, :sec_q2, :sec_a1, :sec_a2);"
            db.execute(query, userid=results[0]["userID"], name=name, email=email, sec_q1=sec_q1,
                       sec_q2=sec_q2,sec_a1=sec_a1,sec_a2=sec_a2)
        except:
            flash('Unexpected database error', 'danger')
            return render_template("register.html")

        flash('Registration complete! Please login with your new credentials.', 'success')
        return redirect("login")


@app.route('/search', methods=["GET", "POST"])
@login_required
def search():
    product = list(request.form["product"].lower())
    name = "%".join(product)
    name = "%" + name + "%"
    category = int(request.form["category"])
    is_custom = "custom" in request.form
    if is_custom:
        if category > 0:
            query = "select customer_products.id,user_id,custom_products.name,category.name as category from " + \
                    "customer_products left join category on category.id=customer_products.cat_id where " + \
                    "user_id=:user_id and cat_id=:category and customer_products.name like :name;"
            results = query_dict(query, user_id=session["userID"], category=category, name=name)
        else:
            query = "select customer_products.id,user_id,customer_products.name,category.name as category " + \
                    "from customer_products left join category on category.id=customer_products.cat_id " + \
                    "where user_id=:user_id and customer_products.name like :name;"
            results = query_dict(query, user_id=session["userID"], name=name)
    else:
        if category > 0:
            query = "select products.id,products.name,category.name as category  from products left join category on category.id=products.cat_id where cat_id=:category and products.name like :name;"
            results = query_dict(query, category=category, name=name)
        else:
            query = "select products.id,products.name,category.name as category  from products left join category on category.id=products.cat_id where products.name like :name;"
            results = query_dict(query, name=name)
    return jsonify(results)
