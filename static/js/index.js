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

    const params = new URLSearchParams(window.location.search);

    console.log("Show Profile:", params.get('show_profile'));

    if (params.get('show_profile') === 'true') {
        console.log("Opening Profile View");

        switchMainView('profileView', $('#profileViewBtn'));
    }

});