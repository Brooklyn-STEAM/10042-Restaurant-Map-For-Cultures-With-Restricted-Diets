# '%%' look for stuff between words
def not_empty(value):
    if value:
        return True
    else:
        return False
def empty_value_filter(values):
    local_values = list(values)
    
    filter_results = filter(not_empty, local_values)
        
    return filter_results

def search_result_return(cursor, base_restaurant_information_sql):
    query = request.args.get("query")
    dietary_restriction_radio = request.args.get("dietary_restriction_radio")

    price_min_filter = request.args.get('price_min_filter')
    price_max_filter = request.args.get('price_max_filter')
    exact_price_toggle = request.args.get("exact_price_toggle")

    search_present = False

    if dietary_restriction_radio:
        search_present = True
        RestaurantDietaryRestriction_JOIN_sql = """
                                                JOIN RestaurantDietaryRestriction
                                                    ON Restaurant.id = RestaurantDietaryRestriction.restaurant_id
                                                """
        WHERE_conditions_sql_radio = f"(RestaurantDietaryRestriction.dietary_restriction_id = {dietary_restriction_radio})"
    else:
        RestaurantDietaryRestriction_JOIN_sql = ""
        WHERE_conditions_sql_radio = ""

    if query: 
        search_present = True
        WHERE_conditions_sql_query = f"""(
                                            (`name` LIKE '%{query}%') 
                                            OR 
                                            (`address` LIKE '%{query}%')
                                            OR 
                                            (`type` LIKE '%{query}%') 
                                            OR 
                                            (`description` LIKE '%{query}%') 
                                            OR 
                                            (`tags` LIKE '%{query}%')
                                        )"""
    else:
        WHERE_conditions_sql_query = ""

    if price_min_filter:
        search_present = True
        if exact_price_toggle:
            WHERE_conditions_sql_price_min_filter = f"(min_cost = {price_min_filter})"
        else:
            WHERE_conditions_sql_price_min_filter = f"(min_cost >= {price_min_filter})"
    else:
        WHERE_conditions_sql_price_min_filter = ""

    if price_max_filter:
        search_present = True
        if exact_price_toggle:
            WHERE_conditions_sql_price_max_filter = f"(max_cost = {price_max_filter})"
        else:
            WHERE_conditions_sql_price_max_filter = f"(max_cost <= {price_max_filter})"
    else:
        WHERE_conditions_sql_price_max_filter = ""
    

    if search_present:
        search_WHERE_conditions_sql_list = [WHERE_conditions_sql_radio, 
                                            WHERE_conditions_sql_query, 
                                            WHERE_conditions_sql_price_min_filter, 
                                            WHERE_conditions_sql_price_max_filter]
        filtered_search_WHERE_conditions_sql_list = empty_value_filter(search_WHERE_conditions_sql_list)
        search_WHERE_conditions_sql =  " WHERE " + " AND ".join(filtered_search_WHERE_conditions_sql_list)
        
        search_restaurant_information_sql = base_restaurant_information_sql + RestaurantDietaryRestriction_JOIN_sql + search_WHERE_conditions_sql + ";"
        
        cursor.execute(search_restaurant_information_sql)
        search_restaurant_results = cursor.fetchall()
        print(search_restaurant_information_sql)
        return search_restaurant_results
    else:
        return None

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
    conn = pymysql.connect(
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

    def __init__(self, id, email, first_name, middle_name, last_name, preferred_name ):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.preferred_name = preferred_name 

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
        return User(result["id"], result["email"], result["first_name"], result["middle_name"], result["last_name"], result["preferred_name"])


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
            flash("Your email/password is incorrect")

        elif password != user_data["password"]:
            flash("Your email/password is incorrect")

        else:
            user = User(user_data["id"], 
                        user_data["email"], 
                        user_data["first_name"], 
                        user_data["middle_name"], 
                        user_data["last_name"],
                        user_data["preferred_name"])
            # use if all user information is needed
            # user = User(user_data["id"], 
            #             user_data["email"], 
            #             user_data["password"], 
            #             user_data["first_name"], 
            #             user_data["middle_name"], 
            #             user_data["last_name"], 
            #             user_data["preferred_name"], 
            #             user_data["phone_number"], 
            #             user_data["address"], 
            #             user_data["profile_image"], 
            #             user_data["date"],)
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
    
    base_restaurant_information_sql = f"""
                SELECT Restaurant.id as restaurant_id,
                        name, 
                        type,  
                        min_cost, 
                        max_cost, 
                        image, 
                        FavoriteRestaurants.id as favorite_restaurants_id,
                        FavoriteRestaurants.user_id 
                FROM Restaurant 
                LEFT JOIN FavoriteRestaurants 
                    ON Restaurant.id = FavoriteRestaurants.restaurant_id 
                        AND FavoriteRestaurants.user_id = {current_user_id}
                """
    
    search_information = search_result_return(cursor, base_restaurant_information_sql)

    # Favorite + Recommendation
    cursor.execute(base_restaurant_information_sql + ";")
    restaurant_information = cursor.fetchall()

    # Dietary Restriction
    cursor.execute("SELECT * FROM DietaryRestriction")
    dietary_restriction_list = cursor.fetchall()

    cursor.close()
    conn.close()

    user_favorite_present = ""
    for restaurant in restaurant_information:
        if restaurant["user_id"] == current_user_id:
            user_favorite_present = "yes"
            break        

    return render_template("restaurant_browser_page.html.jinja", 
                           restaurant_information = restaurant_information,
                           search_information = search_information, 
                           dietary_restriction_list = dietary_restriction_list,
                           user_favorite_present = user_favorite_present)

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
    user_id = flask_login.current_user.id


    cursor.execute(f"SELECT * FROM `Restaurant` WHERE `Restaurant`.`id` = {restaurant_id} ;")
    restaurant_information = cursor.fetchone()

    cursor.execute(f"""
                    SELECT 
                        rating, title, text, Review.date, Review.user_id as reviewer_id,
                        User.first_name,User.middle_name, User.last_name, User.preferred_name 
                    FROM Review 
                    JOIN User 
                        ON User.id = Review.user_id 
                    WHERE restaurant_id = {restaurant_id};
                """)
    review_information = cursor.fetchall()
    def return_current_user_review():
        for review in review_information: 
            if review["reviewer_id"] == user_id:
                return review


    current_user_review = return_current_user_review()

    total_stars = 0
    total_zero_stars = 0
    total_one_stars = 0
    total_two_stars = 0
    total_three_stars = 0
    total_four_stars = 0
    total_five_stars = 0
    for review in review_information:
        total_stars += review["rating"]
        if review["rating"] == 0:
            total_zero_stars += 1
        elif review["rating"] == 1:
            total_one_stars += 1
        elif review["rating"] == 2:
            total_two_stars += 1
        elif review["rating"] == 3:
            total_three_stars += 1
        elif review["rating"] == 4:
            total_four_stars += 1
        elif review["rating"] == 5:
            total_five_stars += 1

    if len(review_information) > 0:
        average_stars = total_stars/len(review_information)
    else:
        average_stars = None

    total_of_each_star_count_list = [total_zero_stars, 
                                total_one_stars, 
                                total_two_stars, 
                                total_three_stars, 
                                total_four_stars, 
                                total_five_stars]

    cursor.close()
    conn.close()
    return render_template("individual_restaurant_page.html.jinja", 
                           restaurant_information = restaurant_information,
                           review_information = review_information, 
                           current_user_review = current_user_review,
                           average_stars = average_stars,
                           total_of_each_star_count_list = total_of_each_star_count_list)

@app.route("/individual_restaurant/<restaurant_id>/review_insert/", methods=["POST", "GET"])
@flask_login.login_required
def restaurant_review_insert(restaurant_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    user_id = flask_login.current_user.id
    restaurant_review_user_rating = request.form["restaurant_review_user_rating"]
    restaurant_review_title = request.form["restaurant_review_title"]
    restaurant_review_text = request.form["restaurant_review_text"]

    cursor.execute(f"""INSERT 
                    INTO `Review` 
                        (`user_id`, `restaurant_id`, `rating`, `title`, `text`) 
                    VALUES 
                        ('{user_id}','{restaurant_id}','{restaurant_review_user_rating}','{restaurant_review_title}', '{restaurant_review_text}') ;
                   """)

    cursor.close()
    conn.close()
    return redirect(f"/individual_restaurant/{restaurant_id}")

@app.route("/individual_restaurant/<restaurant_id>/review_update/", methods=["POST", "GET"])
@flask_login.login_required
def restaurant_review_update(restaurant_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    user_id = flask_login.current_user.id
    restaurant_review_user_rating = request.form["restaurant_review_user_rating"]
    restaurant_review_title = request.form["restaurant_review_title"]
    restaurant_review_text = request.form["restaurant_review_text"]

    cursor.execute(f"""
                   UPDATE Review 
                   SET 
                        rating = {restaurant_review_user_rating}, 
                        title = '{restaurant_review_title}', 
                        text = '{restaurant_review_text}',
                        date = CURRENT_TIMESTAMP
                   WHERE 
                        user_id = {user_id} 
                        AND 
                        restaurant_id = {restaurant_id};
                """)

    cursor.close()
    conn.close()
    return redirect(f"/individual_restaurant/{restaurant_id}")


@app.route("/map" , methods=["POST", "GET"])
def map_page():
    conn = connect_db()
    cursor = conn.cursor()
    current_user_id = flask_login.current_user.id
    
    base_restaurant_information_sql = f"""
                SELECT Restaurant.id as restaurant_id,
                        name, 
                        type, 
                        min_cost, 
                        max_cost, 
                        image, 
                        lng, 
                        lat, 
                        FavoriteRestaurants.id as favorite_restaurants_id,
                        FavoriteRestaurants.user_id 
                FROM Restaurant 
                LEFT JOIN FavoriteRestaurants 
                    ON Restaurant.id = FavoriteRestaurants.restaurant_id 
                        AND FavoriteRestaurants.user_id = {current_user_id}
                """
    
    search_information = search_result_return(cursor, base_restaurant_information_sql)

    # Favorite + Recommendation
    cursor.execute(base_restaurant_information_sql + ";")
    restaurant_information = cursor.fetchall()

    # Dietary Restriction
    cursor.execute("SELECT * FROM DietaryRestriction")
    dietary_restriction_list = cursor.fetchall()

    cursor.close()
    conn.close()

    user_favorite_present = ""
    for restaurant in restaurant_information:
        if restaurant["user_id"] == current_user_id:
            user_favorite_present = "yes"
            break        

    return render_template("map.html.jinja", 
                           restaurant_information = restaurant_information,
                           search_information = search_information, 
                           dietary_restriction_list = dietary_restriction_list,
                           user_favorite_present = user_favorite_present)



@app.route("/contact" , methods=["POST", "GET"])
def contact_page():
    return render_template("contact_page.html.jinja")

@app.route("/about_us" , methods=["POST", "GET"])
def about_us_page():
    return render_template("about_us_page.html.jinja")

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