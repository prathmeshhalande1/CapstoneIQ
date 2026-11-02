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
                <span>Choose your project...</span>
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
$(document).ready(function () {
    getallUserProject();
});