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

function change_currentPagination(change, target_id) {
    const local_change = change
    const local_target_id = target_id

    const target = document.getElementById(target_id)

    target.


    const local_inputElement_id = inputElement_id;
    const input_element = document.getElementById(local_inputElement_id);
    const currentPagination_group = input_element.dataset.group;
    const searchForm = document.getElementById("searchBar_form") 

    // remove name from buttons and inputs of the same group
    const currentPagination_groupmates = document.querySelectorAll("[data-group=" + currentPagination_group + "]");
    currentPagination_groupmates.forEach(groupmates => {
        groupmates.name = ""
    });

    input_element.name = "pagination-" + currentPagination_group

    searchForm.submit()
}