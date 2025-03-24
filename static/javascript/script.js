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