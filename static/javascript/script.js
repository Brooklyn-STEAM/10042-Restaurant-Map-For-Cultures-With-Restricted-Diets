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

async function change_accordionToggleIcon(accordionToggle_id, accordionToggleIcon_id){
    const local_accordionToggleIcon_id = accordionToggleIcon_id;
    const local_accordionToggle_id = accordionToggle_id

    const accordionToggleIcon_element = document.getElementById(local_accordionToggleIcon_id);
    const current_accordionToggleIcon_url = new URL(accordionToggleIcon_element.src).pathname;
    
    if (current_accordionToggleIcon_url == "/static/images/svgs/arrow_down.svg") {
        accordionToggleIcon_element.src = "/static/images/svgs/arrow_up.svg";
    }
    else {
        accordionToggleIcon_element.src = "/static/images/svgs/arrow_down.svg";
    }

    await delay(1000); // Wait for 1 second

    const accordionToggle_element = document.getElementById(local_accordionToggle_id);
    const accordionToggle_class = accordionToggle_element.classList

    if (accordionToggle_class.contains("collapsed")) {
        accordionToggleIcon_element.src = "/static/images/svgs/arrow_down.svg";
    }
    else {
        accordionToggleIcon_element.src = "/static/images/svgs/arrow_up.svg";
    }
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
