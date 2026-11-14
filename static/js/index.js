const { data } = require("jquery");

function switchMainView(viewId, btn) {
    $('#chatView, #analyticsView, #profileView').addClass('d-none').removeClass('d-flex');
    $('#' + viewId).removeClass('d-none').toggleClass('d-flex', viewId === 'chatView');
    $('.navIconBtn').removeClass('active'); $(btn).addClass('active');
    fillOption()
}

function fillOption() {
    dataGroup = sessionStorage.getItem('group')
    dataUser = sessionStorage.getItem('user')

    console.log(dataGroup, dataUser)
}
$(document).ready(function () {
    fillOption()
});