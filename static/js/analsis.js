
let defualtOutput1 = 'Choose your group...';

function selectProjectOption(clickItem, e) {
    if (e) e.preventDefault();

    const $item = $(clickItem);
    const projId = $item.attr('data-id');
    const projTitle = $item.attr('data-title');

    defualtOutput1 = projTitle || 'Choose your group...';
    console.log("Selected Default Output:", defualtOutput1);

    $('#selectedProjectId').val(projId);

    $('#modalProjectDropdownBtn span:first-child').text(defualtOutput1);

    const dropdownToggle = document.getElementById('modalProjectDropdownBtn');
    if (dropdownToggle) {
        const dropdownInstance = bootstrap.Dropdown.getInstance(dropdownToggle) || new bootstrap.Dropdown(dropdownToggle);
        dropdownInstance.hide();
    }

    const scriptTag = document.getElementById('allGroupsData');
    if (!scriptTag) {
        console.warn("⚠️ allGroupsData script tag missing from page!");
        return;
    }
    let group = [];
    try {
        let rawContent = scriptTag.textContent.trim();
        group = JSON.parse(rawContent);
        if (typeof group === 'string') {
            group = JSON.parse(group);
        }
    } catch (e) {
        console.error("❌ Failed to parse group JSON:", e);
    }


    const Data = group.filter(i => String(i.id) === String(projId))
    console.log(Data)
    Data[0].participants = Data[0].participants.filter(user => user.is_creator !== true);
    console.log(Data)
    sessionStorage.setItem('group', JSON.stringify(Data))
}

function getallUserProject() {
    const scriptTag = document.getElementById('allGroupsData');
    if (!scriptTag) {
        console.warn("⚠️ allGroupsData script tag missing from page!");
        return;
    }
    let projects = [];
    try {
        let rawContent = scriptTag.textContent.trim();
        projects = JSON.parse(rawContent);
        if (typeof projects === 'string') {
            projects = JSON.parse(projects);
        }
    } catch (e) {
        console.error("❌ Failed to parse projects JSON:", e);
    }
    console.log("Loaded Projects for Modal:", projects);

    const topProjects = projects.slice(0, 5);

    let listItemsHtml = '';
    topProjects.forEach(group => {
        listItemsHtml += `
            <li>
                <a class="dropdown-item text-white project-option px-2 py-1 mb-1" href="#" 
                   data-id="${group.id}" 
                   data-title="${group.groupName}"
                   onclick="selectProjectOption(this, event)">
                    <div class="fw-bold text-truncate">${group.groupName} <span class="text-secondary text-end">${group.createdAt || 'Active'}</span></div>
                </a>
            </li>
        `;
    });

    const projectOptionHtml = `
        <label class="form-label text-white-50 mt-2">Select Project</label>
        <div class="dropdown w-100">
            <input type="hidden" name="project_id" id="selectedProjectId" value="">
            
            <button class="btn form-select glass-input text-white text-start w-100 d-flex justify-content-between align-items-center" type="button" data-bs-toggle="dropdown" id="modalProjectDropdownBtn">
                <span>${defualtOutput1}</span>
                <span>▼</span>
            </button>
            
            <ul class="dropdown-menu w-100 glass p-2 mt-1" style="background: rgba(20, 20, 30, 0.93);  backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1);">
                <li class="px-2 pb-3 pt-1 border-bottom border-secondary border-opacity-25 sticky-top ">
                    <input type="text" id="groupSearchInput" class="form-control form-control-sm glass-input text-white" placeholder="Search repositories..." onkeyup="filterModalGroup()" style="outline: none; box-shadow: none;">
                </li>
                
                <div id="modalGroupList" class="mt-2"  style="z-index: 100000;">
                    ${listItemsHtml}
                </div>
            </ul>
        </div>
    `;
    console.log($('#groupOption').length);
    const $groupOption = $('#groupOption');
    $groupOption.html(projectOptionHtml);

}
function filterModalGroup() {
    console.log("1")
    const searchText = $('#groupSearchInput').val().toLowerCase();
    const scriptTag = document.getElementById('allGroupsData');
    if (!scriptTag) return;

    let projects = [];
    try {
        projects = JSON.parse(scriptTag.textContent.trim());
        if (typeof projects === 'string') {
            projects = JSON.parse(projects);
        }
    } catch (e) {
        console.error("❌ Parse error:", e);
    }

    if (!Array.isArray(projects)) {
        projects = projects ? [projects] : [];
    }

    const filtered = projects.filter(p => p.groupName.toLowerCase().includes(searchText));
    const $listContainer = $('#modalGroupList');
    $listContainer.empty();

    if (filtered.length === 0) {
        $listContainer.html(`<div class="p-2 text-center text-secondary small">No projects found</div>`);
        return;
    }

    filtered.forEach(group => {
        const itemHtml = `
            <li>
                <a class="dropdown-item text-white project-option px-2 py-1 mb-1 rounded" href="#" 
                   data-id="${group.id}" 
                   data-title="${group.groupName || 'Untitled Project'}"
                   onclick="selectProjectOption(this, event)">
                    <div class="fw-bold text-truncate">${group.groupName || 'Untitled Project'}</div>
                    <small class="text-secondary">${group.createdAt || 'Active'}</small>
                </a>
            </li>
        `;
        $listContainer.append(itemHtml);
    });
}
$(document).ready(function () {
    getallUserProject();
});

let defaultUserOutput = 'Choose your user...';

function selectUserOption(clickItem, e) {
    if (e) e.preventDefault();

    const $item = $(clickItem);
    const userId = $item.attr('data-id');
    const userName = $item.attr('data-username');

    defaultUserOutput = userName || 'Choose your user...';
    console.log("Selected Default User:", defaultUserOutput);

    $('#selectedUserId').val(userId);
    $('#modalUserDropdownBtn span:first-child').text(defaultUserOutput);

    const dropdownToggle = document.getElementById('modalUserDropdownBtn');
    if (dropdownToggle) {
        const dropdownInstance = bootstrap.Dropdown.getInstance(dropdownToggle) || new bootstrap.Dropdown(dropdownToggle);
        dropdownInstance.hide();
    }

    let group = [];
    try {
        group = JSON.parse(sessionStorage.getItem('group') || '[]');
    } catch (e) {
        console.error("Failed to parse group session:", e);
    }

    const participants = group[0]?.participants || [];
    const Data = participants.filter(i => String(i.id) === String(userId));

    console.log(Data);
    sessionStorage.setItem('user', JSON.stringify(Data));
}

function getallGroupUsers() {
    let group = [];

    try {
        group = JSON.parse(sessionStorage.getItem('group') || '[]');
    } catch (e) {
        console.error("Failed to parse group session:", e);
    }

    const participants = group[0]?.participants || [];

    console.log("Loaded Users for Modal:", participants);

    const topUsers = participants.slice(0, 5);

    let listItemsHtml = '';
    topUsers.forEach(user => {
        listItemsHtml += `
            <li>
                <a class="dropdown-item text-white user-option px-2 py-1 mb-1"
                   href="#"
                   data-id="${user.id}"
                   data-username="${user.username} (${user.full_name})"
                   onclick="selectUserOption(this, event)">
                    <div class="fw-bold text-truncate">
                        ${user.username} (${user.full_name})
                    </div>
                </a>
            </li>
        `;
    });

    const userOptionHtml = `
        <label class="form-label text-white-50 mt-2">Select User</label>
        <div class="dropdown w-100">
            <input type="hidden" name="user_id" id="selectedUserId" value="">

            <button class="btn form-select glass-input text-white text-start w-100 d-flex justify-content-between align-items-center"
                    type="button"
                    data-bs-toggle="dropdown"
                    id="modalUserDropdownBtn">
                <span>${defaultUserOutput}</span>
                <span>▼</span>
            </button>

            <ul class="dropdown-menu w-100 glass p-2 mt-1"
                style="background: rgba(20, 20, 30, 0.93); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1);">

                <li class="px-2 pb-3 pt-1 border-bottom border-secondary border-opacity-25 sticky-top">
                    <input type="text"
                           id="userSearchInput"
                           class="form-control form-control-sm glass-input text-white"
                           placeholder="Search users..."
                           onkeyup="filterModalUsers()"
                           style="outline: none; box-shadow: none;">
                </li>

                <div id="modalUserList" class="mt-2" style="z-index: 100000;">
                    ${listItemsHtml}
                </div>
            </ul>
        </div>
    `;

    console.log($('#userOption').length);
    const $userOption = $('#userOption');
    $userOption.html(userOptionHtml);
}

function filterModalUsers() {
    console.log("1");

    const searchText = $('#userSearchInput').val().toLowerCase();

    let group = [];
    try {
        group = JSON.parse(sessionStorage.getItem('group') || '[]');
    } catch (e) {
        console.error("Parse error:", e);
    }

    const participants = group[0]?.participants || [];

    const filtered = participants.filter(user =>
        `${user.username} ${user.full_name}`.toLowerCase().includes(searchText)
    );

    const $listContainer = $('#modalUserList');
    $listContainer.empty();

    if (filtered.length === 0) {
        $listContainer.html(`
            <div class="p-2 text-center text-secondary small">
                No users found
            </div>
        `);
        return;
    }

    filtered.forEach(user => {
        const itemHtml = `
            <li>
                <a class="dropdown-item text-white user-option px-2 py-1 mb-1 rounded"
                   href="#"
                   data-id="${user.id}"
                   data-username="${user.username} (${user.full_name})"
                   onclick="selectUserOption(this, event)">
                    <div class="fw-bold text-truncate">
                        ${user.username} (${user.full_name})
                    </div>
                </a>
            </li>
        `;

        $listContainer.append(itemHtml);
    });
}

$(document).ready(function () {
    getallGroupUsers();
});
