from flask import Flask, render_template, request, redirect, flash, abort
import pymysql
from dynaconf import Dynaconf
import flask_login

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

    def __init__(self, id, email, first_name, last_name):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `User` WHERE `id` = {user_id}")

    result = cursor.fetchone()
    #if there is no vaule in the requested database vaule a None will be returned
    cursor.close()
    conn.close()

    if result is not None:
        return User(result["id"], result["email"], result["first_name"], result["last_name"])

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


@app.route("/sign_in", methods=["POST", "GET"])
def sign_in_page():
    if flask_login.current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM `User` WHERE `email` = '{email}'; ")
        user_data = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if user_data is None:
            flash("Your username/password is incorrect")

        elif password != user_data["password"]:
            flash("Your username/password is incorrect")

        else:
            user = User(user_data["id"], user_data["email"], user_data["first_name"], user_data["last_name"])
            flask_login.login_user(user)
            return redirect('/') 
    
    return render_template("sign_in_page.html.jinja")
    
@app.route('/sign_out')
@flask_login.login_required
def sign_out():
    flask_login.logout_user()
    return redirect('/')

@app.route('/restaurant_browser', methods=["POST", "GET"])
@flask_login.login_required
def restaurant_browser():
    conn = connect_db()
    cursor = conn.cursor()
    current_user_id = flask_login.current_user.id
    
    query = request.args.get("query")
    if query == "":
        query = None
    
    if query == None:
        cursor.execute(f"""
            SELECT Restaurant.id as restaurant_id, 
                    name, 
                    type, 
                    cost, 
                    image, 
                    FavoriteRestaurants.id as favorite_restaurants_id,
                    FavoriteRestaurants.user_id 
            FROM Restaurant 
            LEFT JOIN FavoriteRestaurants 
                ON Restaurant.id = FavoriteRestaurants.restaurant_id 
                    AND FavoriteRestaurants.user_id = {current_user_id};
        """)
        restaurant_information = cursor.fetchall()
        search_information = None
    else:
        cursor.execute(f"""
            SELECT Restaurant.id as restaurant_id, 
                    name, 
                    type, 
                    cost, 
                    image, 
                    FavoriteRestaurants.id as favorite_restaurants_id,
                    FavoriteRestaurants.user_id 
            FROM Restaurant 
            LEFT JOIN FavoriteRestaurants 
                ON Restaurant.id = FavoriteRestaurants.restaurant_id 
                    AND FavoriteRestaurants.user_id = {current_user_id};
        """)
        restaurant_information = cursor.fetchall()

        cursor.execute(f"""
            SELECT Restaurant.id as restaurant_id, 
                    name, 
                    address,
                    type, 
                    cost, 
                    description,
                    image, 
                    tags,
                    FavoriteRestaurants.id as favorite_restaurants_id,
                    FavoriteRestaurants.user_id 
            FROM Restaurant 
            LEFT JOIN FavoriteRestaurants 
                ON Restaurant.id = FavoriteRestaurants.restaurant_id 
                    AND FavoriteRestaurants.user_id = {current_user_id}
            WHERE 
                `name` LIKE '%{query}%' 
                OR 
                `address` LIKE '%{query}%' 
                OR 
                `type` LIKE '%{query}%'
                OR
                `cost` LIKE '%{query}%' 
                OR 
                `description` LIKE '%{query}%' 
                OR 
                `tags` LIKE '%{query}%';
        """)
        #cost search isn't working
        search_information = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template("restaurant_browser_page.html.jinja", 
                           restaurant_information = restaurant_information,
                           search_information = search_information)

@app.route('/restaurant_browser/insert_favorite/<restaurant_id>', methods=["POST", "GET"])
@flask_login.login_required
def insert_favorite(restaurant_id):
    conn = connect_db()
    cursor = conn.cursor()
    user_id = flask_login.current_user.id

    cursor.execute(f"""
    INSERT INTO FavoriteRestaurants 
        ( user_id , restaurant_id )
    VALUES
        ( {user_id}, {restaurant_id} ) ;
    """)

    cursor.close()
    conn.close()

    return redirect("/restaurant_browser")

@app.route('/restaurant_browser/delete_favorite/<favorite_id>', methods=["POST", "GET"])
@flask_login.login_required
def delete_favorite(favorite_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(f"""
        DELETE FROM `FavoriteRestaurants` WHERE `id` = {favorite_id};
    """)

    cursor.close()
    conn.close()

    return redirect("/restaurant_browser")

@app.route("/individual_restaurant/<restaurant_id>")
@flask_login.login_required
def individual_restaurant(restaurant_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Restaurant` WHERE `Restaurant`.`id` = {restaurant_id} ;")
    restaurant_information = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template("individual_restaurant_page.html.jinja", 
                           restaurant_information = restaurant_information)

@app.route("/map")
@flask_login.login_required
def map_page():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.close()
    conn.close()


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