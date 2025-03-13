from flask import Flask, render_template, request, redirect, flash, abort
import pymysql
from dynaconf import Dynaconf
import flask_login
import datetime

app = Flask(__name__) 

conf = Dynaconf(
    settings_file = ["settings.toml"]
)

app.secret_key = conf.secret_key

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = ('/sign_in')

def connect_db():
    conn =pymysql.connect(
        host="db.steamcenter.tech",
        database="dish_map",
        user='bwang',
        password= conf.password,
        autocommit= True,
        cursorclass= pymysql.cursors.DictCursor
    )

    return conn

class User:
    is_authenticated = True
    is_anonymous = False
    is_active = True

    def __init__(self, id, username, email, first_name, last_name):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Customer` WHERE `id` = {user_id}")

    result = cursor.fetchone()
    #if there is no vaule in the requested database vaule a None will be returned
    cursor.close()
    conn.close()

    if result is not None:
        return User(result["id"], result["username"], result["email"], result["first_name"], result["last_name"])


#coordinator connect two fuction
@app.route("/")
def index():
    return render_template("home_page.html.jinja",)

#Authentication
@app.route("/sign_up", methods=["POST", "GET"])
def sign_up_page():
    if flask_login.current_user.is_authenticated:
        return redirect("/")


    if request.method == "POST":
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        preferred_name = request.form["preferred_name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        phone_number = request.form["phone_number"]
        address = request.form["address"]
        
        if len(password) >= 10:
            if password == confirm_password:
                try:
                    conn = connect_db()
                    cursor = conn.cursor()
                    cursor.execute(f"""
                    INSERT INTO `User` 
                        ( `first_name`, `middle_name`, `last_name`, `preferred_name`, `email`, `password`, `phone_number`, `address` )
                    VALUES
                        ( '{first_name}', '{middle_name}', '{last_name}', '{preferred_name}', '{email}', '{password}', '{phone_number}', '{address}' ) ;
                    """)
                    # column names need to be in `ticks`
                except pymysql.err.IntegrityError:
                    flash("Sorry, that preferred name/email is already in use.")
                else:
                    return redirect("/sign_in")
                    #ONLY ONE RETURN WILL BE RUN
                finally:
                    cursor.close()
                    conn.close()
            else:
                flash("Sorry, Password and Confirm Password must match.")
        else:
            flash("Sorry, Your Password need to be stronger: it should be at least 10 characters long")

    return render_template("sign_up_page.html.jinja")


@app.route("/sign_in")
def sign_in_page():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.close()
    conn.close()
    
@app.route('/sign_out')
@flask_login.login_required
def sign_out():
    flask_login.logout_user()
    return redirect('/')







@app.route("/map")
def map_page():
    conn = connect_db()
    cursor = conn.cursor()
   

    cursor.close()
    conn.close()
    return render_template("map.html.jinja")

# @app.route("/cart")
# @flask_login.login_required
# def cart_page():
#     conn = connect_db()
#     cursor = conn.cursor()
#     customer_id = flask_login.current_user.id
    # cursor.execute(f"SELECT * FROM `Customer` WHERE `username` = '{username}' ;")
    #     #there are '' around {username} because its a string

    #     result = cursor.fetchone()
#     cursor.close()
#     conn.close()











