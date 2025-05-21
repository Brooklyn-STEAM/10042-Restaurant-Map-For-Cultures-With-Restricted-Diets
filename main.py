devMode = {
    "on": True
}
# try:
#     if devMode["on"]: print(f"Start: Calculate {section} Max Page")      
# except:
#     if devMode["on"]: print(f"Error: Calculate {section} Max Page")
# else:
#     if devMode["on"]: print(f"success: Calculate {section} Max Page")
# finally:
#     if devMode["on"]: print(f"End: Calculate {section} Max Page")



def return_searchBarSQL(searchBar):
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

def return_culturalDietaryRestrictionSQL(cultural_dietaryRestriction):
    if cultural_dietaryRestriction:
        cultural_dietaryRestriction_SQL = f"(RestaurantDietaryRestriction.dietary_restriction_id = {cultural_dietaryRestriction})"
        return cultural_dietaryRestriction_SQL
    else:
        return ""

def return_minPriceFilterSQL(min_price, exact_price):
    if min_price:
        if exact_price:
            minPrice_operator = " = "
        else:
            minPrice_operator = " >= "

        min_priceFilter_SQL = f"(min_cost {minPrice_operator} {min_price})"
    else:
        min_priceFilter_SQL = ""

    return min_priceFilter_SQL
    
def return_maxPriceFilterSQL(max_price, exact_price):
    if max_price:
        if exact_price:
            maxPrice_operator = " = "
        else:
            maxPrice_operator = " <= "

        max_priceFilter_SQL = f"(min_cost {maxPrice_operator} {max_price})"
    else:
        max_priceFilter_SQL = ""

    return max_priceFilter_SQL

def return_selectSQL(section, current_route, mode_count):
    section: str = str(section)
    current_route: str = str(current_route)
    mode_count: bool = bool(mode_count)
    
    if mode_count:
        alias_str: str = f"{section}_count"

        selectedCol_SQL = f"""
            COUNT(*) AS {alias_str},
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

def return_joinSQL(current_user_id, cultural_dietaryRestriction):
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

def return_whereSQL(current_user, section):
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

        searchBar_SQL = return_searchBarSQL(searchBar)
        cultural_dietaryRestriction_SQL = return_culturalDietaryRestrictionSQL(cultural_dietaryRestriction)
        min_price_SQL = return_minPriceFilterSQL(min_price, exact_price)
        max_price_SQL = return_maxPriceFilterSQL(max_price, exact_price)
        
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

def return_limitSQL(limit, offset, mode_count):
        if mode_count:
            filter_SQL = ""
        else:
            filter_SQL = f"LIMIT {offset} {limit}"
        return filter_SQL

def return_countSQL(current_route, current_user, section):
    current_route = current_route
    current_user = current_user
    section = section

    mode_count = True

    select_SQL = return_selectSQL(section, current_route, mode_count)
    join_SQL = return_joinSQL(current_user["id"], current_user["inputs"]["searchFilters"]["cultural_dietaryRestriction"])
    where_SQL = return_whereSQL(current_user, section)

    countSQL_list = [select_SQL, join_SQL, where_SQL]
    count_SQL = " ".join(filter(None, countSQL_list)) + ";"
    return count_SQL

def return_columnSQL(limit, current_route, current_user, section, offset):
    limit = limit
    current_route = current_route
    current_user = current_user
    section = section
    offset = offset

    mode_count = False

    select_SQL = return_selectSQL(section, current_route, mode_count)
    join_SQL = return_joinSQL(current_user["id"], current_user["inputs"]["searchFilters"]["cultural_dietaryRestriction"])
    where_SQL = return_whereSQL(current_user, section)
    limit_SQL = return_limitSQL(limit, offset, mode_count)

    columnSQL_list = [select_SQL, join_SQL, where_SQL, limit_SQL]
    column_SQL = " ".join(filter(None, columnSQL_list)) + ";"
    return column_SQL

def return_currentUser(current_user_id, request):
    searchBar = request.args.get("query")
    cultural_dietaryRestriction = request.args.get("dietary_restriction_radio")
    min_price = request.args.get('price_min_filter')
    max_price = request.args.get('price_max_filter')
    exact_price = bool(request.args.get("exact_price_toggle"))

    bool(request.args.get("exact_price_toggle"))
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
    def __init__(self, current_user_id: int, request: object, cursor: object, limit: int):
        if devMode["on"]: print("initializing Browser")
        self.limit = limit
        self.current_route = request.path
        self.current_user = return_currentUser(current_user_id, request)
        self.current_userPageInputs = self.current_user["inputs"]["paginations"]

        self.countSQL_dict: dict = {"searches": str, "favorites": str, "recommendations": str}
        self.countInt_dict: dict = {"searches": int, "favorites": int, "recommendations": int}
        self.max_pageInt_dict: dict = {"searches": int, "favorites": int, "recommendations": int}
        self.current_pageInt_dict: dict = {"searches": int, "favorites": int, "recommendations": int}
        self.offset_dict: dict = {"searches": int, "favorites": int, "recommendations": int}
        self.columnSQL_dict: dict = {"searches": str, "favorites": str, "recommendations": str}
        self.columns_dict: dict = {"searches": dict, "favorites": dict, "recommendations": dict}


        if self.current_user["inputs"]["has_searchFilters"]:
            section_list = ["searches", "favorites", "recommendations"]
        else:
            section_list = ["favorites", "recommendations"]

        for section in section_list:
            if devMode["on"]: print(f"Start: Getting {section} Data")

            countSQL_key: str = section
            try:
                if devMode["on"]: print(f"Start: Getting {section} Count SQL")

                count_SQL = return_countSQL(self.current_route, self.current_user, section)      
            except:
                if devMode["on"]: print(f"Error: Getting {section} Count SQL")
                if devMode["on"]: print(count_SQL)
            else:
                if devMode["on"]: print(f"success: Getting {section} Count SQL")

                self.countSQL_dict[countSQL_key] = count_SQL
            finally:
                if devMode["on"]: print(f"End: Getting {section} Count SQL")
                
            countint_key: str = section
            try:
                if devMode["on"]: print(f"Start: Counting {section}")
                
                cursor.execute(self.countSQL_dict[countSQL_key])
                count_dict = dict(cursor.fetchone())
                count_int = count_dict[f"{section}_count"]
                
            except:
                if devMode["on"]: print(f"Error: Counting {section}")
            else:
                if devMode["on"]: print(f"Success: Counting {section}")

                self.countInt_dict[countint_key] = count_int
            finally:
                if devMode["on"]: print(f"End: Counting {section}")

            max_page_key: str = section
            try:
                if devMode["on"]: print(f"Start: Calculate {section} Max Page")
                count_int = (self.countInt_dict[countint_key])
                limit_int = (self.limit)

                max_page_int = ceil(count_int/limit_int)
            except:
                if devMode["on"]: print(f"Error: Calculate {section} Max Page")
            else:
                if devMode["on"]: print(f"Success: Calculate {section} Max Page")

                self.max_pageInt_dict[max_page_key] = max_page_int
            finally:
                if devMode["on"]: print(f"End: Calculate {section} Max Page")

            current_page_key: str = section
            try:
                if devMode["on"]: print(f"Start: Calculate {section} Current Page")
                input_Page_int = int(self.current_userPageInputs[section])
                max_page_int = int(self.max_pageInt_dict[max_page_key])

                if input_Page_int > max_page_int:
                    current_page = max_page_int
                else:
                    current_page = input_Page_int
            except:
                if devMode["on"]: print(f"Error: Calculate {section} Current Page")
            else:
                if devMode["on"]: print(f"Success: Calculate {section} Current Page")
                self.current_pageInt_dict[current_page_key] = current_page
            finally:
                if devMode["on"]: print(f"End: Calculate {section} Current Page")

            offset_key = section
            try:
                if devMode["on"]: print(f"Start: Calculate {section} Offset")
                current_sectionPage_int = int(self.current_pageInt_dict[f"current_{section}Page"])
            except:
                if devMode["on"]: print(f"Error: Calculate {section} Offset")
            else:
                if devMode["on"]: print(f"Success: Calculate {section} Offset")
                self.offset_dict[offset_key] = current_sectionPage_int * 10
            finally:
                if devMode["on"]: print(f"End: Calculate {section} Offset")
            
            
            columnSQL_key = section
            try:
                if devMode["on"]: print(f"Start: Getting {section} Column SQL")

                columnSQL = return_columnSQL(self.limit, self.current_route, self.current_user, section, self.offset_dict[section])
            except:
                if devMode["on"]: print(f"Error: Getting {section} Column SQL")
            else:
                if devMode["on"]: print(f"Success: Getting {section} Column SQL")

                self.columnSQL_dict[columnSQL_key] = columnSQL
            finally:
                if devMode["on"]: print(f"End: Getting {section} Column SQL")
            
            if devMode["on"]: print(f"End: Getting {section} Column SQL")


            columns_key = section
            devLogs: str = f"Querying {section} Columns"
            try:
                if devMode["on"]: print(f"Start: {devLogs}")

                cursor.execute(self.columnSQL_dict[columnSQL_key])
                columns_dict = cursor.fetchall() 
            except:
                if devMode["on"]: print(f"Error: {devLogs}")
            else:
                if devMode["on"]: print(f"Success: {devLogs}")

                self.columns_dict[columns_key] = columns_dict
            finally:
                if devMode["on"]: print(f"End: {devLogs}")
            
            if devMode["on"]: print(f"End: Getting {section} Column SQL")

        if devMode["on"]: print(f"End: Getting {section} Data")
        
        self.public_data = {
            "searches": {
                "results": self.columns_dict["searches"] if self.current_user["inputs"]["has_searchFilters"] else None,
                "count": self.countInt_dict["searches"] if self.current_user["inputs"]["has_searchFilters"] else None,
                "current_page": self.current_pageInt_dict["searches"] if self.current_user["inputs"]["has_searchFilters"] else None,
                "max_page": self.max_pageInt_dict["searches"] if self.current_user["inputs"]["has_searchFilters"] else None
            },
            "favorites":{
                "results": self.columns_dict["favorites"],
                "count": self.countInt_dict["favorites"],
                "current_page": self.current_pageInt_dict["favorites"],
                "max_page": self.max_pageInt_dict["favorites"]
            },
            "recommendations":{
                "results": self.columns_dict["recommendations"],
                "count": self.countInt_dict["recommendations"],
                "current_page": self.current_pageInt_dict["recommendations"],
                "max_page": self.max_pageInt_dict["recommendations"]
            },
            "current_user": self.current_user
        }








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
    
    current_user_id = flask_login.current_user.id
    
    current_browser = Browser(current_user_id, request, cursor, 10)
    browser_publicData = current_browser.public_data


    # Dietary Restriction
    cursor.execute("SELECT * FROM DietaryRestriction")
    dietary_restriction_list = cursor.fetchall()


    cursor.close()
    conn.close()

    return render_template("restaurant_browser_page.html.jinja", 
                            search_results = browser_publicData["searches"]["results"], 
                            current_paginationSearchs_int = browser_publicData["searches"]["current_page"],
                            max_paginationsearchs = browser_publicData["searches"]["max_page"],

                            favorite_results = browser_publicData["favorites"]["results"], 
                            current_paginationFavorites_int = browser_publicData["favorites"]["current_page"],
                            max_paginationFavorites = browser_publicData["favorites"]["max_page"],

                            recommendation_results = browser_publicData["recommendations"]["results"], 
                            current_paginationRecommendations_int = browser_publicData["recommendations"]["current_page"],
                            max_paginationRecommendations = browser_publicData["recommendations"]["max_page"],
                            
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