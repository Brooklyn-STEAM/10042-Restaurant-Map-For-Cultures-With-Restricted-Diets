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

function check_currentPagination(group) {
    const paginationRadio_id = "radio-pagination-current-" + group
    const pagination_radio = document.getElementById(paginationRadio_id)

    pagination_radio.checked = true
}

function turn_currentPagination(target_page_int, input_id) {
    const local_target_page_int = target_page_int
    const local_input_id = input_id
    const input_element = document.getElementById(local_input_id)
    const searchForm_element = document.getElementById("searchBar_form") 

    input_element.value = local_target_page_int

    searchForm_element.submit()
}
