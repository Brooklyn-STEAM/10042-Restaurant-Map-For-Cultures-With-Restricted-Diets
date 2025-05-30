from flask import Flask, render_template, request, redirect, flash
import pymysql
from dynaconf import Dynaconf
import flask_login
from math import ceil
def generate_searchBarSQL(searchBar):
    if searchBar:
        searchBar_SQL = f"""(
            (`name` LIKE '%{searchBar}%') 
            OR 
            (`address` LIKE '%{searchBar}%')
            OR 
            (`type` LIKE '%{searchBar}%') 
            OR 
            (`description` LIKE '%{searchBar}%') 
            OR 
            (`tags` LIKE '%{searchBar}%')
        )"""
        return searchBar_SQL
    else:
        return ""

def generate_culturalDietaryRestrictionSQL(cultural_dietaryRestriction):
    if cultural_dietaryRestriction:
        cultural_dietaryRestriction_SQL = f"(RestaurantDietaryRestriction.dietary_restriction_id = {cultural_dietaryRestriction})"
        return cultural_dietaryRestriction_SQL
    else:
        return ""

def generate_minPriceFilterSQL(min_price, exact_price):
    if min_price:
        if exact_price:
            minPrice_operator = " = "
        else:
            minPrice_operator = " >= "

        min_priceFilter_SQL = f"(min_cost {minPrice_operator} {min_price})"
    else:
        min_priceFilter_SQL = ""

    return min_priceFilter_SQL
    
def generate_maxPriceFilterSQL(max_price, exact_price):
    if max_price:
        if exact_price:
            maxPrice_operator = " = "
        else:
            maxPrice_operator = " <= "

        max_priceFilter_SQL = f"(min_cost {maxPrice_operator} {max_price})"
    else:
        max_priceFilter_SQL = ""

    return max_priceFilter_SQL

def generate_dataItemSQL(key, *dataItems) -> str:
    premadeDIs = {
        "/restaurant_browser": [
            "Restaurant.id as restaurant_id",
            "name", 
            "type",  
            "min_cost", 
            "max_cost", 
            "image", 
            "FavoriteRestaurants.id as favorite_restaurants_id",
            "FavoriteRestaurants.user_id", 
        ],
        "/map": [
            "Restaurant.id as restaurant_id",
            "name", 
            "type",  
            "min_cost", 
            "max_cost", 
            "image", 
            "FavoriteRestaurants.id as favorite_restaurants_id",
            "FavoriteRestaurants.user_id", 
            "lng",
            "lat"
        ]
    }
    base_dataItems = premadeDIs[key]

    base_dataItemSQL_segment = ", \n".join(base_dataItems)
    if dataItems:
        inputted_dataItemSQL_segment = ", \n".join(dataItems)
        dataItem_SQL =  base_dataItemSQL_segment + ", " + inputted_dataItemSQL_segment
    else:
        dataItem_SQL = base_dataItemSQL_segment

    return dataItem_SQL



def generate_selectSQL(section, current_route, mode_count):
    if mode_count:
        alias_str: str = f"{section}_count"
        dataItem_SQL = f"""
            COUNT(*) AS {alias_str}
        """            
    else:    
        dataItem_SQL = generate_dataItemSQL(current_route)

    select_SQL = f"""
        SELECT 
            {dataItem_SQL}
        FROM Restaurant
    """
    return select_SQL


def generate_joinSQL(current_user_id, cultural_dietaryRestriction):
    if cultural_dietaryRestriction:
        join_SQL = f"""
            LEFT JOIN FavoriteRestaurants 
                ON Restaurant.id = FavoriteRestaurants.restaurant_id 
                    AND FavoriteRestaurants.user_id = {current_user_id}
            JOIN RestaurantDietaryRestriction
                ON Restaurant.id = RestaurantDietaryRestriction.restaurant_id

        """
    else:
        join_SQL = f"""
            LEFT JOIN FavoriteRestaurants 
                ON Restaurant.id = FavoriteRestaurants.restaurant_id 
                    AND FavoriteRestaurants.user_id = {current_user_id}
        """

    return join_SQL

def generate_whereSQL(current_user, section):
    current_user = current_user
    current_user_id = current_user["id"]
    current_userInputs = current_user["inputs"]
    
    FishMap_SQL = """
        Restaurant.id != 0
    """
    if section == "searches" and current_userInputs["has_searchFilters"]:
        searchBar = current_userInputs["searchFilters"]["searchBar"]
        cultural_dietaryRestriction = current_userInputs["searchFilters"]["cultural_dietaryRestriction"]
        min_price = current_userInputs["searchFilters"]["min_price"]
        max_price = current_userInputs["searchFilters"]["max_price"]
        exact_price = current_userInputs["searchFilters"]["exact_price"]

        searchBar_SQL = generate_searchBarSQL(searchBar)
        cultural_dietaryRestriction_SQL = generate_culturalDietaryRestrictionSQL(cultural_dietaryRestriction)
        min_price_SQL = generate_minPriceFilterSQL(min_price, exact_price)
        max_price_SQL = generate_maxPriceFilterSQL(max_price, exact_price)
        
        filterSQL_list = [
            FishMap_SQL,
            searchBar_SQL, 
            cultural_dietaryRestriction_SQL, 
            min_price_SQL,
            max_price_SQL
        ]
        filter_SQL = " AND ".join(filter(None, filterSQL_list))
    elif section == "favorites":
        favOnly_SQL = f"FavoriteRestaurants.user_id = {current_user_id}"
        
        filterSQL_list = [
            FishMap_SQL,
            favOnly_SQL, 
        ]
        filter_SQL = " AND ".join(filter(None, filterSQL_list))
    else:
        filter_SQL = FishMap_SQL

    where_SQL = "WHERE" + " " + filter_SQL
    return where_SQL

def generate_limitSQL(limit, offset, mode_count):
        if mode_count:
            filter_SQL = ""
        else:
            filter_SQL = f"LIMIT {offset}, {limit}"
        return filter_SQL

def generate_countSQL(current_route, current_user, section):
    current_route = current_route
    current_user = current_user
    section = section

    mode_count = True

    select_SQL = generate_selectSQL(section, current_route, mode_count)
    join_SQL = generate_joinSQL(current_user["id"], current_user["inputs"]["searchFilters"]["cultural_dietaryRestriction"])
    where_SQL = generate_whereSQL(current_user, section)

    countSQL_list = [select_SQL, join_SQL, where_SQL]
    count_SQL = " ".join(filter(None, countSQL_list)) + ";"
    print(count_SQL)
    return count_SQL

def generate_columnSQL(limit, current_route, current_user, section, offset):
    limit = limit
    current_route = current_route
    current_user = current_user
    section = section
    offset = offset

    mode_count = False

    select_SQL = generate_selectSQL(section, current_route, mode_count)
    join_SQL = generate_joinSQL(current_user["id"], current_user["inputs"]["searchFilters"]["cultural_dietaryRestriction"])
    where_SQL = generate_whereSQL(current_user, section)
    limit_SQL = generate_limitSQL(limit, offset, mode_count)

    columnSQL_list = [select_SQL, join_SQL, where_SQL, limit_SQL]
    column_SQL = " ".join(filter(None, columnSQL_list)) + ";"
    return column_SQL

def generate_currentUser(current_user_id, request):
    searchBar = request.args.get("query")
    cultural_dietaryRestriction = request.args.get("dietary_restriction_radio")
    min_price = request.args.get('price_min_filter')
    max_price = request.args.get('price_max_filter')
    exact_price = bool(request.args.get("exact_price_toggle"))

    curr_searchesPagination = request.args.get("pagination-searchs")
    curr_favoritesPagination = request.args.get("pagination-favorites")
    curr_recommendationsPagination = request.args.get("pagination-recommendations")

    current_user = {
        "id": current_user_id,
        "inputs": {
            "searchFilters": {
                "searchBar": searchBar,
                "cultural_dietaryRestriction": cultural_dietaryRestriction,
                "min_price": min_price,
                "max_price": max_price,
                "exact_price": exact_price,
            },

            "has_searchFilters": True if searchBar or cultural_dietaryRestriction or min_price or max_price else False,

            "paginations": {
                "searches": curr_searchesPagination if curr_searchesPagination else "1", # fix spelling
                "favorites": curr_favoritesPagination if curr_favoritesPagination else "1",
                "recommendations": curr_recommendationsPagination if curr_recommendationsPagination else "1"
            }
        }
    }
    return current_user


class Browser:
    def generate_countInt(self, section):
        section = str(section)

        # COUNT SQL
        count_SQL = str(generate_countSQL(self.current_route, self.current_user, section))
        
        # COUNT INT
        self.cursor.execute(count_SQL)
        count_dict = dict(self.cursor.fetchone())

        count_int = count_dict[f"{section}_count"]
        return int(count_int)
    
    def calc_maxPage(self, count_int):
        # MAX PAGE
        count_int = int(count_int)
        
        limit_int = int(self.limit)

        max_page = ceil(count_int / limit_int)
        return int(max_page)    
    
    def calc_currentPage(self, section, max_page):
        # CURRENT PAGE
        section = str(section)
        max_page = int(max_page)

        input_page = int(self.current_user["inputs"]["paginations"][section])

        if input_page > max_page:
            current_page = max_page
        else:
            current_page = input_page
        
        return int(current_page)
    
    def calc_offsetInt(self, current_page):
        # OFFSET INT
        offset_int = (current_page - 1) * 10
        return int(offset_int)
    
    def generate_results(self, section, offset_int):
        # COLUMN SQL
        results_SQL = str(generate_columnSQL(self.limit, self.current_route, self.current_user, section, offset_int))

        # COLUMN LIST
        self.cursor.execute(results_SQL)
        results_list = self.cursor.fetchall() 
        return list(results_list)

    def __init__(self, current_user_id: int, request: object, cursor: object, limit: int):
        self.current_route = request.path
        self.current_user = generate_currentUser(current_user_id, request)

        self.cursor = cursor
        self.limit = limit

        self.public_data = {
            "counts": {"searches": int, "favorites": int, "recommendations": int},
            "max_pages": {"searches": int, "favorites": int, "recommendations": int},
            "curr_pages": {"searches": int, "favorites": int, "recommendations": int},
            "results": {"searches": [], "favorites": [], "recommendations": []},
            "given_filter": bool(self.current_user["inputs"]["has_searchFilters"]),
            "curr_user_id": current_user_id
        }


        section_list = ["recommendations"]
        if self.current_user["inputs"]["has_searchFilters"]:
            section_list += ["searches"]
        if self.current_user["id"]:
            section_list += ["favorites"]

        for section in section_list:
            count_int = self.generate_countInt(section)
            max_page = self.calc_maxPage(count_int)
            curr_page = self.calc_currentPage(section, max_page)
            offset_int = self.calc_offsetInt(curr_page)
            results = self.generate_results(section, offset_int)

            self.public_data["counts"][section] = count_int
            self.public_data["max_pages"][section] = max_page
            self.public_data["curr_pages"][section] = curr_page
            self.public_data["results"][section] = list(results)

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
    
    current_browser = Browser(current_user_id, request, cursor, 10)
    browser_publicData = current_browser.public_data


    # Dietary Restriction
    cursor.execute("SELECT * FROM DietaryRestriction")
    dietary_restriction_list = cursor.fetchall()


    cursor.close()
    conn.close()

    return render_template("restaurant_browser_page.html.jinja", 
                            browser_publicData = browser_publicData,
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
    
    current_browser = Browser(current_user_id, request, cursor, 10)
    browser_publicData = current_browser.public_data


    # Dietary Restriction
    cursor.execute("SELECT * FROM DietaryRestriction")
    dietary_restriction_list = cursor.fetchall()


    cursor.close()
    conn.close()

    return render_template("map.html.jinja", 
                            browser_publicData = browser_publicData,
                            dietary_restriction_list = dietary_restriction_list)



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