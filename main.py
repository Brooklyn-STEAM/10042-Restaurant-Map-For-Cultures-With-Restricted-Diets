devMode = {
    "on": True
}
class generate_universalSQL:
    def __init__(self, section, current_route):
        self.section = section
        self.current_route = current_route

    def generate_selectSQL(self, mode_count):
        section = self.section
        current_route = self.current_route
        mode_count = mode_count
        
        if mode_count:
            if section == "searches":
                selectedCol_SQL = """
                    COUNT(*) AS searchesResultRows_int
                """
            elif section == "favorites":
                selectedCol_SQL = """
                    COUNT(FavoriteRestaurants.user_id = 1) AS allResultRows_int,
                    COUNT(*) AS favoritesResultRows_int
                """
            elif section == "recommendations":
                selectedCol_SQL = """
                    COUNT(FavoriteRestaurants.user_id = 1) AS allResultRows_int,
                    COUNT(*) AS favoritesResultRows_int
                """
            else:
                selectedCol_SQL = """
                    COUNT(FavoriteRestaurants.user_id = 1) AS allResultRows_int,
                    COUNT(*) AS favoritesResultRows_int
                """
        else:
            if current_route == "/restaurant_browser":
                selectedCol_SQL = """
                    Restaurant.id as restaurant_id,
                    name, 
                    type,  
                    min_cost, 
                    max_cost, 
                    image, 
                    FavoriteRestaurants.id as favorite_restaurants_id,
                    FavoriteRestaurants.user_id 
                """
            elif current_route == "/map":
                selectedCol_SQL = """
                    Restaurant.id as restaurant_id,
                    name, 
                    type,  
                    min_cost, 
                    max_cost, 
                    image, 
                    FavoriteRestaurants.id as favorite_restaurants_id,
                    FavoriteRestaurants.user_id, 
                    lng,
                    lat
                """
        select_SQL = f"""
            SELECT 
                {selectedCol_SQL}
            FROM Restaurant
        """
        return select_SQL
    
    def generate_joinSQL(self, cultural_dietaryRestriction):
        current_user_id = self.current_user["id"]
        cultural_dietaryRestriction = cultural_dietaryRestriction
        
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


class generate_searchesSQL:
    def __init__(self, current_user, current_route, limit):
        self.current_user = current_user
        self.current_route = current_route
        self.limit = limit
        self.generate_universalSQL = generate_universalSQL("searches", self.current_route)


        if self.limit:
            self.mode_count = True
        else:
            self.mode_count = False

    

    def generate_searchBarFilterSQL(self):
        searchBar = self.current_user["inputs"]["searchFilters"]["searchBar"]

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
    
    def generate_culturalDietaryRestrictionSQL(self):
        cultural_dietaryRestriction = self.current_user["inputs"]["searchFilters"]["cultural_dietaryRestriction"]

        cultural_dietaryRestriction_SQL = f"(RestaurantDietaryRestriction.dietary_restriction_id = {cultural_dietaryRestriction})"

        return cultural_dietaryRestriction_SQL


    def generate_minPriceFilterSQL(self):
        min_price = self.current_user["inputs"]["searchFilters"]["min_price"]
        exact_price = self.current_user["inputs"]["searchFilters"]["exact_price"]

        if exact_price:
            if exact_price:
                minPrice_operator = " = "
            else:
                minPrice_operator = " >= "

            min_PriceFilter_SQL = f"(min_cost {minPrice_operator} {min_price})"
        else:
            min_PriceFilter_SQL = ""

        return min_PriceFilter_SQL
    
    def generate_maxPriceFilterSQL(self):
        max_price = self.current_user["inputs"]["searchFilters"]["max_price"]
        exact_price = self.current_user["inputs"]["searchFilters"]["exact_price"]

        if max_price:
            if exact_price:
                maxPrice_operator = " = "
            else:
                maxPrice_operator = " <= "

            max_PriceFilter_SQL = f"(min_cost {maxPrice_operator} {maxPrice_operator})"
        else:
            max_PriceFilter_SQL = ""

        return max_PriceFilter_SQL

    def generate_whereSQL(self):
        searchBarFilter_SQL = self.generate_searchBarFilterSQL()
        cultural_dietaryRestriction_SQL = self.generate_culturalDietaryRestrictionSQL()
        min_PriceFilter_SQL = self.generate_minPriceFilterSQL()
        max_PriceFilter_SQL = self.generate_maxPriceFilterSQL()
        FishMap_SQL = """
            Restaurant.id != 0
        """

        filterSQL_list = [
            FishMap_SQL,
            searchBarFilter_SQL, 
            cultural_dietaryRestriction_SQL, 
            min_PriceFilter_SQL,
            max_PriceFilter_SQL
        ]
        filter_SQL = " AND ".join(filter(None, filterSQL_list))

        where_SQL = "WHERE" + " " + filter_SQL
        return where_SQL
    
    def return_searchSQL(self):
        select_SQL = self.generate_selectSQL()
        join_SQL = self.generate_joinSQL()
        where_sql = self.generate_whereSQL()

        search_SQL = select_SQL + join_SQL + where_sql
        return search_SQL
    


    

    
    





class Browser:
    def __init__(self, current_user_id, request, limit):
        self.limit = limit
        self.current_route = request.path

        self.current_user = {
            "id": current_user_id,
            "inputs": {
                "searchFilters": {
                    "searchBar": request.args.get("query"),
                    "cultural_dietaryRestriction": request.args.get("dietary_restriction_radio"),
                    "min_price": request.args.get('price_min_filter'),
                    "max_price": request.args.get('price_max_filter'),
                    "exact_price": bool(request.args.get("exact_price_toggle")),
                },

                "has_searchFilters": False,

                "pagination": {
                    "searches": request.args.get("pagination-searchs"), # fix spelling
                    "favorites": request.args.get("pagination-favorites"),
                    "recommendations": request.args.get("pagination-recommendations")
                }
            }
        }

        for key in dict.keys(self.userInputs["searchFilters"]):
            if self.userInputs["searchFilters"][key] and key != "exact_price":
                self.userInputs["has"] = True
        
        self.generate_SQL = {
            "searches": {
                "columns": generate_searchesSQL(self.current_user, self.current_route, self.limit),
                "count":  generate_searchesSQL(self.current_user, self.current_route, False)
            },
            "favorites": {

            },
            "recommendations": {

            }

            
        }

    def __str__(self):
        return self.request
    
    def return_browserData(self):
        browser_data = {
            "searches": {
                "results": "<--Replace-->",
                "count": "<--Replace-->",
                "current_page": "<--Replace-->",
                "max_page": "<--Replace-->"
            },
            "favorites":{
                "results": "<--Replace-->",
                "count": "<--Replace-->",
                "current_page": "<--Replace-->",
                "max_page": "<--Replace-->"
            },
            "recommendations":{
                "results": "<--Replace-->",
                "count": "<--Replace-->",
                "current_page": "<--Replace-->",
                "max_page": "<--Replace-->"
            },
            "has_searchFilters": self.current_user["has_searchFilters"]
        }
        return browser_data
    
    def generate_selectedColSQL(self, section, mode_count):
        local_current_route = self.current_route

        local_section = section
        local_mode_count = mode_count
        
        if local_mode_count:
            if local_section == "searches":
                selectedCol_SQL = """
                    COUNT(*) AS searchesResultRows_int
                """
            elif local_section == "allNfav":
                selectedCol_SQL = """
                    COUNT(FavoriteRestaurants.user_id = 1) AS allResultRows_int,
                    COUNT(*) AS favoritesResultRows_int
                """
        else:
            # normal
            selectedCol_SQL = """
                Restaurant.id as restaurant_id,
                name, 
                type,  
                min_cost, 
                max_cost, 
                image, 
                FavoriteRestaurants.id as favorite_restaurants_id,
                FavoriteRestaurants.user_id 
            """
            # Mini Browser
            if local_current_route == "/map":
                mapCol_SQL = """
                    lng,
                    lat
                """
                selectedCol_SQL += mapCol_SQL

        selectedColSQL = selectedCol_SQL
        return selectedColSQL


    def generate_selectSQL(self, section, mode_count):
        local_section = section
        local_mode_count = mode_count

        selectedCol_SQL = self.generate_selectedColSQL(local_section, local_mode_count)

        select_SQL = f"""
            SELECT 
                {selectedCol_SQL}
            FROM Restaurant
        """

        selectSQL = select_SQL
        return selectSQL
    
    def generate_joinSQL(self):
        local_current_user_id = self.current_user_id
        join_SQL = f"""
            LEFT JOIN FavoriteRestaurants 
                ON Restaurant.id = FavoriteRestaurants.restaurant_id 
                    AND FavoriteRestaurants.user_id = {local_current_user_id}
        """

        joinSQL = join_SQL
        return joinSQL
    











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
def return_searchSQL(currentUser_id, query, dietaryRestriction_id, minFilter_price, maxFilter_price, exactPrice_toggle, offset_int, count_bool, limit_num):
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

        price_SQLlist = [minPrice_SQL, maxPrice_SQL]

        price_SQL = " AND ".join(empty_value_filter(price_SQLlist))

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
    local_limit_num = limit_num
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
        dietaryRestrictionSQL = ""

    if local_query:
        querySQL = return_querySQL(local_query)
    else:
        querySQL = ""

    if local_minFilter_price or local_maxFilter_price:
        price_SQL = return_price_SQL(local_minFilter_price, local_maxFilter_price, local_exactPrice_toggle)
    else:
        price_SQL = ""

    search_sqlParts = [dietaryRestrictionSQL, querySQL, price_SQL]

    if local_dietaryRestriction_id:
        search_WHEREsql = " AND ".join(empty_value_filter(search_sqlParts))
    else:
        search_WHEREsql = " WHERE" + " AND ".join(empty_value_filter(search_sqlParts))
        

    if local_count_bool:
        search_SQL = baseRestaurantInfo_SQL + search_WHEREsql + ";"
    else:
        search_SQL = baseRestaurantInfo_SQL + search_WHEREsql + f" LIMIT {local_offset_int},{local_limit_num};"
    
    return search_SQL

def return_currentPage(pagination_value, maxPage_number):
    local_pagination_value = pagination_value
    local_maxPage_number = maxPage_number

    try:
        local_pagination_value = int(local_pagination_value)
    except:
        local_pagination_value =  1

    if local_pagination_value > local_maxPage_number:
        currentPage = local_maxPage_number
    elif local_pagination_value < 1:
        currentPage = 1
    else:
        currentPage = local_pagination_value
    return currentPage


from flask import Flask, render_template, request, redirect, flash
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

    paginationSearchs_value = request.args.get("pagination-searchs")
    paginationFavorites_value = request.args.get("pagination-favorites")
    paginationRecommendations_value = request.args.get("pagination-recommendations")

    limit = 10
    cursor.execute(f"""SELECT COUNT(FavoriteRestaurants.user_id = 1) AS "favNum", COUNT(*) AS "allNum"
                FROM Restaurant
                LEFT JOIN FavoriteRestaurants ON 
                    Restaurant.id = FavoriteRestaurants.restaurant_id AND FavoriteRestaurants.user_id = {currentUser_id};
    """)
    fav_rec_count = cursor.fetchone()
    max_paginationFavorites = ceil(fav_rec_count["favNum"] / limit)
    max_paginationRecommendations = ceil(fav_rec_count["allNum"] / limit)

    if query or dietaryRestriction_id or minFilter_price or maxFilter_price:
        searchOffset_int = 0
        searchCOUNT_SQL = return_searchSQL(currentUser_id, query, dietaryRestriction_id, minFilter_price, maxFilter_price, exactPrice_radioToggle, searchOffset_int, True, limit)
        cursor.execute(searchCOUNT_SQL)
        searchCOUNT_resultRaw = cursor.fetchone()
        max_paginationSearchs = ceil(searchCOUNT_resultRaw["searchAll"] / limit)

        if max_paginationSearchs < 1:
            max_paginationSearchs = 1
        
    else:
        max_paginationSearchs = 1


    current_paginationSearchs_int = return_currentPage(paginationSearchs_value, max_paginationSearchs)
    current_paginationFavorites_int = return_currentPage(paginationFavorites_value, max_paginationFavorites)
    current_paginationRecommendations_int = return_currentPage(paginationRecommendations_value, max_paginationRecommendations)

    searchOffset_int = limit * (current_paginationSearchs_int - 1)
    favoriteOffset_int = limit * (current_paginationFavorites_int - 1)
    recommendationOffset_int = limit * (current_paginationRecommendations_int - 1)



    if query or dietaryRestriction_id or minFilter_price or maxFilter_price:
        search_SQL = return_searchSQL(currentUser_id, query, dietaryRestriction_id, minFilter_price, maxFilter_price, exactPrice_radioToggle, searchOffset_int, False, limit)
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
                LIMIT {favoriteOffset_int}, {limit};
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
                LIMIT {recommendationOffset_int}, {limit};
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
                            max_paginationsearchs = max_paginationSearchs,

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

    currentUser_id = flask_login.current_user.id
    
    query = request.args.get("query")
    dietaryRestriction_id = request.args.get("dietary_restriction_radio")

    minFilter_price = request.args.get('price_min_filter')
    maxFilter_price = request.args.get('price_max_filter')
    exactPrice_radioToggle = request.args.get("exact_price_toggle")

    paginationSearchs_value = request.args.get("pagination-searchs")
    paginationFavorites_value = request.args.get("pagination-favorites")
    paginationRecommendations_value = request.args.get("pagination-recommendations")

    limit = 10

    cursor.execute(f"""SELECT COUNT(FavoriteRestaurants.user_id = 1) AS "favNum", COUNT(*) AS "allNum"
                FROM Restaurant
                LEFT JOIN FavoriteRestaurants ON 
                    Restaurant.id = FavoriteRestaurants.restaurant_id AND FavoriteRestaurants.user_id = {currentUser_id};
    """)
    fav_rec_count = cursor.fetchone()
    max_paginationFavorites = ceil(fav_rec_count["favNum"] / limit)
    max_paginationRecommendations = ceil(fav_rec_count["allNum"] / limit)

    if query or dietaryRestriction_id or minFilter_price or maxFilter_price:
        searchOffset_int = 0
        searchCOUNT_SQL = return_searchSQL(currentUser_id, query, dietaryRestriction_id, minFilter_price, maxFilter_price, exactPrice_radioToggle, searchOffset_int, True, limit)
        cursor.execute(searchCOUNT_SQL)
        searchCOUNT_resultRaw = cursor.fetchone()
        max_paginationSearchs = ceil(searchCOUNT_resultRaw["searchAll"] / limit)

        if max_paginationSearchs < 1:
            max_paginationSearchs = 1
        
    else:
        max_paginationSearchs = 1


    current_paginationSearchs_int = return_currentPage(paginationSearchs_value, max_paginationSearchs)
    current_paginationFavorites_int = return_currentPage(paginationFavorites_value, max_paginationFavorites)
    current_paginationRecommendations_int = return_currentPage(paginationRecommendations_value, max_paginationRecommendations)

    searchOffset_int = limit * (current_paginationSearchs_int - 1)
    favoriteOffset_int = limit * (current_paginationFavorites_int - 1)
    recommendationOffset_int = limit * (current_paginationRecommendations_int - 1)



    if query or dietaryRestriction_id or minFilter_price or maxFilter_price:
        search_SQL = return_searchSQL(currentUser_id, query, dietaryRestriction_id, minFilter_price, maxFilter_price, exactPrice_radioToggle, searchOffset_int, False, limit)
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
                LIMIT {favoriteOffset_int}, {limit};
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
                LIMIT {recommendationOffset_int}, {limit};
                """)
    recommendation_results = cursor.fetchall()

    # Dietary Restriction
    cursor.execute("SELECT * FROM DietaryRestriction")
    dietary_restriction_list = cursor.fetchall()


    cursor.close()
    conn.close()

    return render_template("map.html.jinja", 
                            search_results = search_results, 
                            current_paginationSearchs_int = current_paginationSearchs_int,
                            max_paginationsearchs = max_paginationSearchs,

                            favorite_results = favorite_results, 
                            current_paginationFavorites_int = current_paginationFavorites_int,
                            max_paginationFavorites = max_paginationFavorites,

                            recommendation_results = recommendation_results, 
                            current_paginationRecommendations_int = current_paginationRecommendations_int,
                            max_paginationRecommendations = max_paginationRecommendations,
                            
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