let defualtOutput = 'Choose your project...';

function selectProjectOption(clickItem, e) {
    if (e) e.preventDefault();

    const $item = $(clickItem);
    const projId = $item.attr('data-id');
    const projTitle = $item.attr('data-title');

    defualtOutput = projTitle || 'Choose your project...';
    console.log("Selected Default Output:", defualtOutput);

    $('#selectedProjectId').val(projId);

    $('#modalProjectDropdownBtn span:first-child').text(defualtOutput);

    const dropdownToggle = document.getElementById('modalProjectDropdownBtn');
    if (dropdownToggle) {
        const dropdownInstance = bootstrap.Dropdown.getInstance(dropdownToggle) || new bootstrap.Dropdown(dropdownToggle);
        dropdownInstance.hide();
    }
}

function getallUserProject() {
    const scriptTag = document.getElementById('userProjectsData');
    if (!scriptTag) {
        console.warn("⚠️ userProjectsData script tag missing from page!");
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
    topProjects.forEach(project => {
        listItemsHtml += `
            <li>
                <a class="dropdown-item text-white project-option px-2 py-1 mb-1" href="#" 
                   data-id="${project.id}" 
                   data-title="${project.title}"
                   onclick="selectProjectOption(this, event)">
                    <div class="fw-bold text-truncate">${project.title} <span class="text-secondary text-end">${project.status || 'Active'}</span></div>
                </a>
            </li>
        `;
    });

    const projectOptionHtml = `
        <label class="form-label text-white-50 mt-2">Select Project</label>
        <div class="dropdown w-100">
            <input type="hidden" name="project_id" id="selectedProjectId" value="">
            
            <button class="btn form-select glass-input text-white text-start w-100 d-flex justify-content-between align-items-center" type="button" data-bs-toggle="dropdown" id="modalProjectDropdownBtn">
                <span>${defualtOutput}</span>
                <span>▼</span>
            </button>
            
            <ul class="dropdown-menu w-100 glass p-2 mt-1" style="background: rgba(20, 20, 30, 0.93); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1);">
                <li class="px-2 pb-3 pt-1 border-bottom border-secondary border-opacity-25 sticky-top ">
                    <input type="text" id="projectSearchInput" class="form-control form-control-sm glass-input text-white" placeholder="Search repositories..." onkeyup="filterModalProjects()" style="outline: none; box-shadow: none;">
                </li>
                
                <div id="modalProjectList" class="mt-2">
                    ${listItemsHtml}
                </div>
            </ul>
        </div>
    `;
    console.log($('#pojectOption').length);
    const $pojectOption = $('#pojectOption');
    $pojectOption.html(projectOptionHtml);

}
function filterModalProjects() {
    const searchText = $('#projectSearchInput').val().toLowerCase();
    const scriptTag = document.getElementById('userProjectsData');
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

    const filtered = projects.filter(p => p.title.toLowerCase().includes(searchText));
    const $listContainer = $('#modalProjectList');
    $listContainer.empty();

    if (filtered.length === 0) {
        $listContainer.html(`<div class="p-2 text-center text-secondary small">No projects found</div>`);
        return;
    }

    filtered.forEach(project => {
        const itemHtml = `
            <li>
                <a class="dropdown-item text-white project-option px-2 py-1 mb-1 rounded" href="#" 
                   data-id="${project.id}" 
                   data-title="${project.title || 'Untitled Project'}"
                   onclick="selectProjectOption(this, event)">
                    <div class="fw-bold text-truncate">${project.title || 'Untitled Project'}</div>
                    <small class="text-secondary">${project.status || 'Active'}</small>
                </a>
            </li>
        `;
        $listContainer.append(itemHtml);
    });
}
$(document).ready(function () {
    getallUserProject();
});