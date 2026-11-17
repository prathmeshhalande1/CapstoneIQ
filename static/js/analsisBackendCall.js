function refreshTelemetry() {
    const groupId = $('#selectedProjectId').val();
    const userId = $('#selectedUserId').val();
    const userData = JSON.parse(sessionStorage.getItem('user') || '[]');
    const refreshBtn = $('#refreshTelemetryBtn');
    refreshBtn.prop('disabled', true).text('Syncing...');
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
            if (response.status === true) {
                console.log("Repository all commit:", response.all_commits);
                console.log("Repository summay:", response.analytics)
                console.log("Repository ", response.language_usage)
                updateTelemetryDashboard(response);
                console.log("Telemetry updated successfully!");
            } else {
                console.log("Telemetry update failed:", response.message);
            }
        },
        error: function (xhr, status, error) {
            console.log("Status Code:", xhr.status);
            console.log("AJAX Status:", status);
            console.log("Error:", error);
            console.log("Response:", xhr.responseText);
        },
        complete: function () {
            refreshBtn.prop('disabled', false).text('Refresh Telemetry');
        }
    });
}

let languageChartInstance = null;
let commitGrowthChartInstance = null;
function updateTelemetryDashboard(response) {
    // 1. Repository summary
    const summary = response.analytics || {};
    $('#metricOutliersCount').text(
        (Number(summary.z_score_outliers || 0) +
            Number(summary.iqr_outliers || 0)) + ' Outliers'
    );
    $('#zScoreOutliers').text(summary.z_score_outliers || 0);
    $('#iqrOutliers').text(summary.iqr_outliers || 0);
    $('#totalLocMetric').text(
        '+' + Number(summary.total_added || 0).toLocaleString() + ' LOC'
    );

    const languages = response.language_usage || {};
    const sortedLanguages = Object.entries(languages)
        .sort((a, b) => b[1] - a[1]);
    const topThree = sortedLanguages.slice(0, 3);
    const otherLanguages = sortedLanguages.slice(3);
    let languageHTML = '';
    topThree.forEach(([name, percentage], index) => {
        languageHTML += `
            <div class="d-flex justify-content-between
                        align-items-center mb-2">
                <span class="text-white fw-bold">
                    ${name}
                </span>
                <span style="color: #818cf8;">
                    ${Number(percentage).toFixed(2)}%
                </span>
            </div>
        `;
    });
    $('#topLanguagesContainer').html(
        languageHTML || '<p class="text-muted">No language data</p>'
    );
    $('#otherLanguagesList').text(
        otherLanguages.map(item => item[0]).join(', ') || 'None'
    );
    // 3. Language doughnut chart
    const languageCanvas = document.getElementById('languageChart');
    if (languageCanvas) {
        if (languageChartInstance) {
            languageChartInstance.destroy();
        }
        languageChartInstance = new Chart(languageCanvas, {
            type: 'doughnut',
            data: {
                labels: sortedLanguages.map(item => item[0]),
                datasets: [{
                    data: sortedLanguages.map(item => item[1]),
                    backgroundColor: [
                        '#3776AB',
                        '#F7DF1E',
                        '#E34F26',
                        '#1572B6',
                        '#28A745',
                        '#9333EA',
                        '#EC4899'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return context.label + ': ' +
                                    context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Commit growth chart
    const commits = [...(response.processed_commits || [])];
    commits.sort((a, b) =>
        new Date(a.commitdata) - new Date(b.commitdata)
    );
    const dailyData = {};
    commits.forEach(commit => {
        const date = commit.commitdata;
        if (!dailyData[date]) {
            dailyData[date] = {
                added: 0,
                deleted: 0
            };
        }
        dailyData[date].added += Number(commit.addline || 0);
        dailyData[date].deleted += Number(commit.deletline || 0);
    });

    const dates = Object.keys(dailyData);
    const addedData = dates.map(date => dailyData[date].added);
    const deletedData = dates.map(date => dailyData[date].deleted);
    const commitCanvas = document.getElementById('commitGrowthChart');
    if (commitCanvas) {
        if (commitGrowthChartInstance) {
            commitGrowthChartInstance.destroy();
        }
        commitGrowthChartInstance = new Chart(commitCanvas, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'Lines Added',
                        data: addedData,
                        borderColor: '#22c55e',
                        backgroundColor: 'rgba(34,197,94,0.15)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Lines Deleted',
                        data: deletedData,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239,68,68,0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff'
                        }
                    }
                },

                scales: {
                    x: {
                        ticks: {
                            color: '#aaaaaa'
                        },
                        grid: {
                            color: 'rgba(255,255,255,0.05)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#aaaaaa'
                        },
                        grid: {
                            color: 'rgba(255,255,255,0.05)'
                        }
                    }
                }
            }
        });
    }

    // Update chart context
    $('#activeChartContext').text(
        'Group: ' + ($('#selectedProjectId').val() || 'All') +
        ' | User: ' + ($('#selectedUserId').val() || 'All')
    );
    console.log('Dashboard updated successfully');
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