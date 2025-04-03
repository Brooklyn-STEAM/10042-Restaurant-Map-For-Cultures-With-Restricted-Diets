function clearSearchBar() {
    const restaurantBrowserSearchBar = document.getElementById("restaurantBrowserSearchBar");
    restaurantBrowserSearchBar.value = ""
};
function clearCulturalDietaryRestrictionRadio() {
    const CulturalDietaryRestrictionRadios = document.getElementsByClassName("filter-radio")
    for (let index = 0; index < CulturalDietaryRestrictionRadios.length; index++) {
        const CulturalDietaryRestrictionRadio = CulturalDietaryRestrictionRadios[index];
        CulturalDietaryRestrictionRadio.checked = false
    }
}
function clearPriceFilterSettings() {
    const priceFilter_money = document.getElementsByClassName("price-filter");
    for (let index = 0; index < priceFilter_money.length; index++) {
        const current_price_filter = priceFilter_money[index];
        current_price_filter.value = ""
    };

    const exact_price_toggle_checkBox = document.getElementById("exact_price_toggle_checkBox");
    exact_price_toggle_checkBox.checked = false
}

function clearAllFilters() {
    clearSearchBar()
    clearCulturalDietaryRestrictionRadio()
    clearPriceFilterSettings()
}

function deleteFavorite(card_id, favoriteRestaurants_id) {
    const _card_id = card_id
    const _favoriteRestaurants_id = favoriteRestaurants_id
    const individualRestaurants_card = document.getElementById(_card_id)
    individualRestaurants_card.remove()
    deleteFavorite_route(_favoriteRestaurants_id)
}
async function deleteFavorite_route(_favoriteRestaurants_id) {
    _favoriteRestaurants_id = favoriteRestaurants_id
    const deleteFavorite_baseRoute = "/restaurant_browser/delete_favorite/"
    const url = deleteFavorite_baseRoute + _favoriteCard_id;
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }
  
      const json = await response.json();
      console.log(json);
    } catch (error) {
      console.error(error.message);
    }
}
function insertFavorite(card_id, restaurants_id) {
    const _card_id = card_id
    const _restaurants_id = restaurants_id
    const individualRestaurants_card = document.getElementById(_card_id)
    individualRestaurants_card.remove()
    insertFavorite_route(_restaurants_id)
}
async function insertFavorite_route(restaurants_id) {
    _restaurants_id = restaurants_id
    const insertFavorite_baseRoute = "/restaurant_browser/insert_favorite/"
    const url = insertFavorite_baseRoute + _restaurants_id;
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }
  
      const json = await response.json();
      console.log(json);
    } catch (error) {
      console.error(error.message);
    }
}
_topButton_containers = document.getElementsByClassName("header-card-topButtons")
for (topButton_container of _topButton_containers) {
    topButton_container.data-
}
fetch('/components/navbar.html.jinja')
    .then(response => response.text())
    .then(html => {
    document.getElementById('hi').innerHTML = html;
    });