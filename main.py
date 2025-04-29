# '%%' look for stuff between words
def empty_value_filter(values):
    def not_empty(value):
        if value:
            return True
        else:
            return False
    local_values = list(values)
    
    filter_results = filter(not_empty, local_values)
        
    return filter_results
def return_searchSQL(currentUser_id, query, dietaryRestriction_id, minFilter_price, maxFilter_price, exactPrice_toggle, offset_int, count_bool):
    def return_price_SQL(minFilter, maxFilter, exactPrice):
        local_minFilter = minFilter
        local_maxFilter = maxFilter
        local_exactPrice = exactPrice
        
        if local_exactPrice:
            minPrice_operator = " = "
            maxPrice_operator = " = "
        else:
            minPrice_operator = " >= "
            maxPrice_operator = " <= "


        if local_minFilter:
            minPrice_SQL = f"(min_cost {minPrice_operator} {local_minFilter})"
        else:
            minPrice_SQL = ""

        if local_maxFilter:
            maxPrice_SQL = f"(max_cost {maxPrice_operator} {local_maxFilter})"
        else:
            maxPrice_SQL = ""

        
        if local_minFilter and local_maxFilter:
            price_SQL = "(" + minPrice_SQL + " AND " + maxPrice_SQL + ")"
        elif local_minFilter:
            price_SQL = minPrice_SQL
        elif local_maxFilter:
            price_SQL = maxPrice_SQL
        else:
            price_SQL = ""

    
        return price_SQL
    def return_querySQL(query):
        local_query = query
        query_SQL = f"""(
                        (`name` LIKE '%{local_query}%') 
                        OR 
                        (`address` LIKE '%{local_query}%')
                        OR 
                        (`type` LIKE '%{local_query}%') 
                        OR 
                        (`description` LIKE '%{local_query}%') 
                        OR 
                        (`tags` LIKE '%{local_query}%')
                    )"""
        return query_SQL
    def return_dietaryRestrictionSQL(dietaryRestriction_id):
        local_dietaryRestriction_id = dietaryRestriction_id
        RestaurantDietaryRestriction_JOINsql = """
                                                JOIN RestaurantDietaryRestriction
                                                    ON Restaurant.id = RestaurantDietaryRestriction.restaurant_id
                                                """
        dietaryRestriction_WHEREsql = f"(RestaurantDietaryRestriction.dietary_restriction_id = {local_dietaryRestriction_id})"

        dietaryRestriction_SQL = RestaurantDietaryRestriction_JOINsql + " WHERE " + dietaryRestriction_WHEREsql

        return dietaryRestriction_SQL
    
    local_currentUser_id = currentUser_id
    local_query = query
    local_dietaryRestriction_id = dietaryRestriction_id
    local_minFilter_price = minFilter_price
    local_maxFilter_price = maxFilter_price
    local_exactPrice_toggle = exactPrice_toggle
    try:
        local_offset_int = offset_int
    except:
        local_offset_int = ""
    local_count_bool = count_bool

    if local_count_bool:
        baseRestaurantInfo_SQL = f"""
                            SELECT 
                                COUNT(*) AS searchAll
                        FROM Restaurant 
                        LEFT JOIN FavoriteRestaurants 
                            ON Restaurant.id = FavoriteRestaurants.restaurant_id 
                                AND FavoriteRestaurants.user_id = {local_currentUser_id}
                """
    else:
        baseRestaurantInfo_SQL = f"""
                            SELECT 
                                Restaurant.id as restaurant_id,
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
                                AND FavoriteRestaurants.user_id = {local_currentUser_id}
                """


    if local_dietaryRestriction_id:
        dietaryRestrictionSQL = return_dietaryRestrictionSQL(local_dietaryRestriction_id)
    else:
        dietaryRestrictionSQL = " WHERE "

    if local_query:
        querySQL = return_querySQL(local_query)
    else:
        querySQL = ""

    if local_minFilter_price or local_maxFilter_price:
        price_SQL = return_price_SQL(local_minFilter_price, local_maxFilter_price, local_exactPrice_toggle)
    else:
        price_SQL = ""

    search_sqlParts = [dietaryRestrictionSQL, querySQL, price_SQL]
    search_WHEREsql = " AND ".join(empty_value_filter(search_sqlParts))

    if local_count_bool:
        search_SQL = baseRestaurantInfo_SQL + search_WHEREsql + ";"
    else:
        search_SQL = baseRestaurantInfo_SQL + search_WHEREsql + f" LIMIT {local_offset_int},10;"
    
    
    
    
    
    
    print("bar")
    print(search_SQL)
    return search_SQL

def return_currentPage(radio_value, maxPage_number, selectedPage_number):
    local_radio_value = radio_value
    local_maxPage_number = maxPage_number
    local_selectedPage_number =  selectedPage_number

    if local_radio_value == "back":
        currentPage = local_selectedPage_number - 1
        if currentPage <= 0:
            currentPage = 1
    elif local_radio_value == "min":
        currentPage = 1
    elif local_radio_value == "current":
        currentPage = local_selectedPage_number
    elif local_radio_value == "max":
        currentPage = local_maxPage_number
    elif local_radio_value == "forward":
        currentPage = local_selectedPage_number + 1
        if currentPage > local_maxPage_number:
            currentPage = local_maxPage_number
    else:
        currentPage = 1
    
    return currentPage


from flask import Flask, render_template, request, redirect, flash, abort
import pymysql
from dynaconf import Dynaconf
import flask_login
from math import ceil

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

    currentUser_id = flask_login.current_user.id
    
    query = request.args.get("query")
    dietaryRestriction_id = request.args.get("dietary_restriction_radio")

    minFilter_price = request.args.get('price_min_filter')
    maxFilter_price = request.args.get('price_max_filter')
    exactPrice_radioToggle = request.args.get("exact_price_toggle")

    paginationSearchs_radio = request.args.get("pagination-searchs")
    paginationFavorites_radio = request.args.get("pagination-favorites")
    paginationRecommendations_radio = request.args.get("pagination-recommendations")

    selected_paginationSearchs = request.args.get("selected-page-searchs")
    selected_paginationFavorites = request.args.get("selected-page-favorites")
    selected_paginationRecommendations = request.args.get("selected-page-recommendations")

    cursor.execute(f"""SELECT COUNT(FavoriteRestaurants.user_id = 1) AS "favNum", COUNT(*) AS "allNum"
                FROM Restaurant
                LEFT JOIN FavoriteRestaurants ON 
                    Restaurant.id = FavoriteRestaurants.restaurant_id AND FavoriteRestaurants.user_id = {currentUser_id};
    """)
    fav_rec_count = cursor.fetchone()
    max_paginationFavorites = ceil(fav_rec_count["favNum"] / 10)
    max_paginationRecommendations = ceil(fav_rec_count["allNum"] / 10)

    if query or dietaryRestriction_id or minFilter_price or maxFilter_price:
        searchOffset_int = 0
        searchCOUNT_SQL = return_searchSQL(currentUser_id, query, dietaryRestriction_id, minFilter_price, maxFilter_price, exactPrice_radioToggle, searchOffset_int, True)
        cursor.execute(searchCOUNT_SQL)
        searchCOUNT_resultRaw = cursor.fetchone()
        searchCOUNT_result = ceil(searchCOUNT_resultRaw["searchAll"] / 10)
        
    else:
        searchCOUNT_result = 1
    try:
        current_paginationSearchs_int = return_currentPage(paginationSearchs_radio, searchCOUNT_result, selected_paginationSearchs)
    except:
        current_paginationSearchs_int = 1

    current_paginationFavorites_int = return_currentPage(paginationFavorites_radio, max_paginationFavorites, selected_paginationFavorites)
    current_paginationRecommendations_int = return_currentPage(paginationRecommendations_radio, max_paginationRecommendations, selected_paginationRecommendations)


    searchOffset_int = 10 * (current_paginationSearchs_int - 1)
    favoriteOffset_int = 10 * (current_paginationFavorites_int - 1)
    recommendationOffset_int = 10 * (current_paginationRecommendations_int - 1)



    if query or dietaryRestriction_id or minFilter_price or maxFilter_price:
        search_SQL = return_searchSQL(currentUser_id, query, dietaryRestriction_id, minFilter_price, maxFilter_price, exactPrice_radioToggle, searchOffset_int, False)
        cursor.execute(search_SQL)
        search_results = cursor.fetchall()
    else:
        search_results = ""

    # Favorite 
    cursor.execute(f"""
                SELECT Restaurant.id as restaurant_id,
                        name, 
                        type,  
                        min_cost, 
                        max_cost, 
                        image, 
                        FavoriteRestaurants.id as favorite_restaurants_id,
                        FavoriteRestaurants.user_id 
                FROM Restaurant 
                JOIN FavoriteRestaurants 
                    ON Restaurant.id = FavoriteRestaurants.restaurant_id 
                        AND FavoriteRestaurants.user_id = {currentUser_id}
                LIMIT {favoriteOffset_int}, 10;
                """)
    favorite_results  = cursor.fetchall()
    # Recommendation
    cursor.execute(f"""
                SELECT  
                    id,
                    name, 
                    type,  
                    min_cost, 
                    max_cost, 
                    image 
                FROM Restaurant 
                LIMIT {recommendationOffset_int}, 10;
                """)
    recommendation_results = cursor.fetchall()

    # Dietary Restriction
    cursor.execute("SELECT * FROM DietaryRestriction")
    dietary_restriction_list = cursor.fetchall()


    cursor.close()
    conn.close()

    return render_template("restaurant_browser_page.html.jinja", 
                            search_results = search_results, 
                            current_paginationSearchs_int = current_paginationSearchs_int,
                            max_paginationsearchs = searchCOUNT_result,

                            favorite_results = favorite_results, 
                            current_paginationFavorites_int = current_paginationFavorites_int,
                            max_paginationFavorites = max_paginationFavorites,

                            recommendation_results = recommendation_results, 
                            current_paginationRecommendations_int = current_paginationRecommendations_int,
                            max_paginationRecommendations = max_paginationRecommendations,
                            
                            dietary_restriction_list = dietary_restriction_list)

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
    
    search_information = search_sql_return(cursor, base_restaurant_information_sql)

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