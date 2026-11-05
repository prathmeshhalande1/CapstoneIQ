function applyGroupFilters() {
    console.log("Search key pressed!");
    const searchText = $('#groupSearchInput').val().toLowerCase();
    console.log("Search key:", searchText)
    $('.groupItem').each(function () {
        const groupName = $(this).attr('data-name');
        console.log(groupName)
        if (groupName) {
            const lowerName = groupName.toLowerCase();
            if (lowerName.includes(searchText)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        }
    });
}
$(document).on('click', '.status-option', function (e) {
    e.preventDefault();
    const selectedValue = $(this).attr('data-value');
    const selectedText = $(this).text();

    $('#statusInput').val(selectedValue);
    $('#statusDropdownBtn').text(selectedText);

    renderGroupSidebar();
});

function renderGroupSidebar() {
    const searchText = $('#groupSearchInput').val().toLowerCase();
    const sortValue = $('#statusInput').val();
    const scriptTag = document.getElementById('allGroupsData');

    if (!scriptTag) return;
    let groups = JSON.parse(scriptTag.textContent);

    let filteredGroups = groups.filter(group =>
        group.groupName.toLowerCase().includes(searchText)
    );


    if (sortValue === 'name-asc') {
        filteredGroups.sort((a, b) => a.groupName.localeCompare(b.groupName));
    } else if (sortValue === 'name-desc') {
        filteredGroups.sort((a, b) => b.groupName.localeCompare(a.groupName));
    } else {
        filteredGroups.sort((a, b) => b.id - a.id);
    }

    $('#visible-group-count').text(filteredGroups.length);

    const $groupList = $('#groupList');
    $groupList.empty();

    if (filteredGroups.length === 0) {
        $groupList.html(`
            <div class="p-4 text-center text-secondary">
                <p class="mb-1">💬 No groups found</p>
                <small>Try a different search keyword.</small>
            </div>
        `);
        return;
    }

    filteredGroups.forEach((group, index) => {
        const isActive = (group.groupCode === activeGroupCode) ? 'active' : '';
        const groupInitial = group.groupName.charAt(0).toUpperCase();

        const groupCardHtml = `
            <div class="groupItem ${isActive}" 
                data-code="${group.groupCode}"
                data-name="${group.groupName}"
                onclick="selectGroupCard('${group.groupCode}', this)">
                
                <div class="d-flex align-items-center gap-3 mb-1">
                    <div class="groupAvatar">${groupInitial}</div>
                    <div class="flex-grow-1 min-w-0">
                        <div class="d-flex justify-content-between align-items-center">
                            <h6 class="fw-bold mb-0 text-truncate text-white">${group.groupName}</h6>
                            <span class="badge bg-primary bg-opacity-25 text-info small">${group.category_badge}</span>
                        </div>
                    </div>
                </div>

                <div class="d-flex justify-content-between align-items-center my-1">
                    <small class="text-secondary">➕ ${group.groupCode} Code</small>
                    <small class="text-light badge bg-secondary bg-opacity-25">👥 ${group.participant_count}</small>
                </div>
            </div>
        `;
        $groupList.append(groupCardHtml);
    });
}
let activeGroupCode = null;
function selectGroupCard(groupCode, element) {
    $('.groupItem').removeClass('active');
    $(element).addClass('active');

    activeGroupCode = groupCode;

    const scriptTag = document.getElementById('allGroupsData');
    if (!scriptTag) return;
    const groups = JSON.parse(scriptTag.textContent);

    const selectedGroup = groups.find(g => g.groupCode === groupCode);
    const singleChar = selectedGroup.groupName[0]
    if (selectedGroup) {
        console.log("Selected Group:", selectedGroup);
        $('#activeGroupName').text(selectedGroup.groupName);
        $('#activeGroupBadge').text(selectedGroup.category_badge);
        $('#activeGroupCode').text(selectedGroup.groupCode);
        $('#activeGroupAvatar').text(singleChar);
        $('#activeGroupCount').text(selectedGroup.participant_count);

    }
}
$(document).ready(function () {
    renderGroupSidebar();
});
