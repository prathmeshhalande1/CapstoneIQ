
function switchMainView(viewId, btn) {
    $('#chatView, #analyticsView, #profileView').addClass('d-none').removeClass('d-flex');
    $('#' + viewId).removeClass('d-none').toggleClass('d-flex', viewId === 'chatView');
    $('.navIconBtn').removeClass('active'); $(btn).addClass('active');
}
