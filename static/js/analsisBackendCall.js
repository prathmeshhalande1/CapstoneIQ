function refreshTelemetry() {
    const groupId = $('#selectedProjectId').val();
    const userId = $('#selectedUserId').val();
    const userData = JSON.parse(sessionStorage.getItem('user') || '[]');
    $.ajax({
        url: '/your-backend-route',
        type: 'POST',
        data: {
            group_id: groupId,
            user_id: userId,
            user: JSON.stringify(userData)
        },
        success: function (response) {
            console.log("Telemetry Response:", response);
        },
        error: function (error) {
            console.error("Telemetry Error:", error);
        }
    });
}

$('#refreshTelemetryBtn').on('click', function () {
    refreshTelemetry();
});