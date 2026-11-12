function refreshTelemetry() {
    const groupId = $('#selectedProjectId').val();
    const userId = $('#selectedUserId').val();
    const userData = JSON.parse(sessionStorage.getItem('user') || '[]');
    $.ajax({
        url: '/Telemetry/get-user-group-repositories/',
        type: 'POST',
        headers: {
        'X-CSRFToken': getCookie('csrftoken')
        },
        data: {
            group_id: groupId,
            user_id: userId,
            user: JSON.stringify(userData)
        },
        success: function (response) {
            console.log("Repository URLs:", response.repository_urls);
        },
        error: function (xhr, status, error) {
            console.log("Status Code:", xhr.status);
            console.log("AJAX Status:", status);
            console.log("Error:", error);
            console.log("Response:", xhr.responseText);
        }
    });
}

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }

    return cookieValue;
}

$('#refreshTelemetryBtn').on('click', function () {
    refreshTelemetry();
});