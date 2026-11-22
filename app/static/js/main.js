// JobHelper AI — Client-side Interactivity
document.addEventListener("DOMContentLoaded", function () {
  // 1. Sidebar Toggle for Mobile
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("appSidebar");
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", function () {
      sidebar.classList.toggle("show");
    });
  }

  // 2. Drag & Drop File Upload Handling
  const dropzone = document.getElementById("uploadDropzone");
  const fileInput = document.getElementById("resumeFileInput");
  const fileNameDisplay = document.getElementById("selectedFileName");
  const uploadForm = document.getElementById("resumeUploadForm");
  const uploadSpinner = document.getElementById("uploadSpinner");
  const uploadSubmitBtn = document.getElementById("uploadSubmitBtn");

  if (dropzone && fileInput) {
    ["dragenter", "dragover"].forEach(eventName => {
      dropzone.addEventListener(eventName, function (e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach(eventName => {
      dropzone.addEventListener(eventName, function (e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove("dragover");
      });
    });

    dropzone.addEventListener("drop", function (e) {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        fileInput.files = files;
        updateFileDisplay(files[0]);
      }
    });

    dropzone.addEventListener("click", function () {
      fileInput.click();
    });

    fileInput.addEventListener("change", function () {
      if (fileInput.files.length > 0) {
        updateFileDisplay(fileInput.files[0]);
      }
    });

    function updateFileDisplay(file) {
      if (fileNameDisplay) {
        const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
        fileNameDisplay.innerHTML = `<strong>Selected:</strong> ${file.name} (${sizeMb} MB)`;
        fileNameDisplay.classList.remove("d-none");
      }
      if (uploadSubmitBtn) {
        uploadSubmitBtn.disabled = false;
      }
    }

    if (uploadForm) {
      uploadForm.addEventListener("submit", function () {
        if (uploadSpinner) {
          uploadSpinner.classList.remove("d-none");
        }
        if (uploadSubmitBtn) {
          uploadSubmitBtn.disabled = true;
          uploadSubmitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Extracting & Analyzing Resume...';
        }
      });
    }
  }

  // 3. Dynamic Form Rows for Resume Builder
  window.addExperienceRow = function () {
    const container = document.getElementById("experienceList");
    if (!container) return;
    const div = document.createElement("div");
    div.className = "card p-3 mb-3 border bg-light item-row";
    div.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <h6 class="mb-0 text-primary"><i class="bi bi-briefcase me-1"></i> Position</h6>
        <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.closest('.item-row').remove()"><i class="bi bi-trash"></i> Remove</button>
      </div>
      <div class="row g-2">
        <div class="col-md-6">
          <label class="form-label small">Job Title / Role</label>
          <input type="text" name="exp_role[]" class="form-control form-control-sm" placeholder="e.g. Senior Software Engineer" required>
        </div>
        <div class="col-md-6">
          <label class="form-label small">Company Name</label>
          <input type="text" name="exp_company[]" class="form-control form-control-sm" placeholder="e.g. Acme Corp">
        </div>
        <div class="col-12">
          <label class="form-label small">Duration</label>
          <input type="text" name="exp_duration[]" class="form-control form-control-sm" placeholder="e.g. 2022 - Present">
        </div>
        <div class="col-12">
          <label class="form-label small">Responsibilities / Achievements</label>
          <textarea name="exp_description[]" class="form-control form-control-sm" rows="3" placeholder="• Architected microservices with Python and Flask&#10;• Reduced latency by 35% across 50k daily active users"></textarea>
        </div>
      </div>
    `;
    container.appendChild(div);
  };

  window.addProjectRow = function () {
    const container = document.getElementById("projectsList");
    if (!container) return;
    const div = document.createElement("div");
    div.className = "card p-3 mb-3 border bg-light item-row";
    div.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <h6 class="mb-0 text-primary"><i class="bi bi-code-slash me-1"></i> Project</h6>
        <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.closest('.item-row').remove()"><i class="bi bi-trash"></i> Remove</button>
      </div>
      <div class="row g-2">
        <div class="col-md-6">
          <label class="form-label small">Project Title</label>
          <input type="text" name="proj_title[]" class="form-control form-control-sm" placeholder="e.g. E-Commerce Recommender Engine" required>
        </div>
        <div class="col-md-6">
          <label class="form-label small">Tech Stack</label>
          <input type="text" name="proj_tech[]" class="form-control form-control-sm" placeholder="e.g. Python, Scikit-learn, Flask, React">
        </div>
        <div class="col-12">
          <label class="form-label small">Description</label>
          <textarea name="proj_description[]" class="form-control form-control-sm" rows="2" placeholder="Engineered high-accuracy collaborative filtering recommendation pipeline."></textarea>
        </div>
      </div>
    `;
    container.appendChild(div);
  };

  window.addEducationRow = function () {
    const container = document.getElementById("educationList");
    if (!container) return;
    const div = document.createElement("div");
    div.className = "card p-3 mb-3 border bg-light item-row";
    div.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <h6 class="mb-0 text-primary"><i class="bi bi-mortarboard me-1"></i> Education</h6>
        <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.closest('.item-row').remove()"><i class="bi bi-trash"></i> Remove</button>
      </div>
      <div class="row g-2">
        <div class="col-md-5">
          <label class="form-label small">Degree / Major</label>
          <input type="text" name="edu_degree[]" class="form-control form-control-sm" placeholder="e.g. B.S. in Computer Science" required>
        </div>
        <div class="col-md-5">
          <label class="form-label small">University / Institution</label>
          <input type="text" name="edu_institution[]" class="form-control form-control-sm" placeholder="e.g. Stanford University">
        </div>
        <div class="col-md-2">
          <label class="form-label small">Graduation Year</label>
          <input type="text" name="edu_year[]" class="form-control form-control-sm" placeholder="e.g. 2024">
        </div>
      </div>
    `;
    container.appendChild(div);
  };
});
