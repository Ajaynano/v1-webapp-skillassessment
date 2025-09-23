// Skills Assessment Integration for existing Angular app
(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeSkillsAssessment();
    });

    function initializeSkillsAssessment() {
        // Check if we're on the skill-assessment page
        if (!window.location.pathname.includes('skill-assessment')) {
            return;
        }

        // Wait for Angular to load, then integrate
        setTimeout(() => {
            integrateWithExistingGrid();
            addSkillsAssessmentFeatures();
        }, 2000);
    }

    function addSkillsAssessmentFeatures() {
        // Create a container for the skills assessment functionality
        const container = document.createElement('div');
        container.id = 'skills-assessment-api-container';
        container.className = 'mt-4';
        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h4>Skills Assessment Management</h4>
                </div>
                <div class="card-body">
                    <!-- Quick Add Form -->
                    <div class="row mb-4">
                        <div class="col-md-12">
                            <h5>Quick Add Assessment</h5>
                            <form id="quickAddForm" class="row g-3">
                                <div class="col-md-3">
                                    <input type="text" class="form-control" id="quickEmployee" placeholder="Employee Name" required>
                                </div>
                                <div class="col-md-2">
                                    <input type="text" class="form-control" id="quickSkill" placeholder="Skill" required>
                                </div>
                                <div class="col-md-2">
                                    <select class="form-control" id="quickCurrent" required>
                                        <option value="">Current</option>
                                        <option value="Beginner">Beginner</option>
                                        <option value="Intermediate">Intermediate</option>
                                        <option value="Advanced">Advanced</option>
                                        <option value="Expert">Expert</option>
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <select class="form-control" id="quickTarget" required>
                                        <option value="">Target</option>
                                        <option value="Beginner">Beginner</option>
                                        <option value="Intermediate">Intermediate</option>
                                        <option value="Advanced">Advanced</option>
                                        <option value="Expert">Expert</option>
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <button type="submit" class="btn btn-primary">Add Assessment</button>
                                    <button type="button" class="btn btn-secondary ms-2" onclick="loadAssessmentsList()">Refresh</button>
                                </div>
                            </form>
                        </div>
                    </div>

                    <!-- Assessments List -->
                    <div class="row">
                        <div class="col-md-12">
                            <h5>Current Assessments</h5>
                            <div id="assessmentsList" class="row">
                                <div class="col-12 text-center">
                                    <div class="spinner-border" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Find a good place to insert the container
        const mainContent = document.querySelector('main') || 
                           document.querySelector('.container') || 
                           document.querySelector('#app') ||
                           document.body;
        
        mainContent.appendChild(container);

        // Initialize event handlers
        setupEventHandlers();
        
        // Load initial data
        loadAssessmentsList();
        
        // Also try to populate existing AG Grid
        populateExistingGrid();
    }

    function setupEventHandlers() {
        const form = document.getElementById('quickAddForm');
        if (form) {
            form.addEventListener('submit', handleQuickAdd);
        }
    }

    async function handleQuickAdd(e) {
        e.preventDefault();
        
        const formData = {
            SkillAssessmentId: generateId(),
            Employee: document.getElementById('quickEmployee').value,
            Skill: document.getElementById('quickSkill').value,
            Current: document.getElementById('quickCurrent').value,
            Target: document.getElementById('quickTarget').value
        };

        try {
            await window.skillsAPI.create(formData);
            document.getElementById('quickAddForm').reset();
            showNotification('Assessment added successfully!', 'success');
            loadAssessmentsList();
            populateExistingGrid(); // Also update the main AG Grid
        } catch (error) {
            console.error('Error adding assessment:', error);
            showNotification('Error adding assessment: ' + error.message, 'error');
        }
    }

    async function loadAssessmentsList() {
        const container = document.getElementById('assessmentsList');
        if (!container) return;

        try {
            container.innerHTML = '<div class="col-12 text-center"><div class="spinner-border" role="status"></div></div>';
            
            const assessments = await window.skillsAPI.list();
            
            if (!assessments || assessments.length === 0) {
                container.innerHTML = '<div class="col-12"><p class="text-muted text-center">No assessments found.</p></div>';
                return;
            }

            container.innerHTML = assessments.map(assessment => `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">${assessment.Employee}</h6>
                            <p class="card-text small">
                                <strong>Skill:</strong> ${assessment.Skill}<br>
                                <span class="badge bg-info">${assessment.Current}</span>
                                <i class="fas fa-arrow-right mx-1"></i>
                                <span class="badge bg-success">${assessment.Target}</span>
                            </p>
                            <button class="btn btn-sm btn-outline-danger" 
                                    onclick="deleteAssessmentItem('${assessment.SkillAssessmentId}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading assessments:', error);
            container.innerHTML = '<div class="col-12"><p class="text-danger text-center">Error loading assessments</p></div>';
        }
    }

    async function deleteAssessmentItem(id) {
        if (!confirm('Are you sure you want to delete this assessment?')) {
            return;
        }

        try {
            await window.skillsAPI.delete(id);
            showNotification('Assessment deleted successfully!', 'success');
            loadAssessmentsList();
        } catch (error) {
            console.error('Error deleting assessment:', error);
            showNotification('Error deleting assessment: ' + error.message, 'error');
        }
    }

    function generateId() {
        return 'SA_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    function showNotification(message, type) {
        // Create a simple notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    function integrateWithExistingGrid() {
        // Try to find and integrate with existing AG Grid
        const gridElements = document.querySelectorAll('[class*="ag-grid"], [class*="ag-root"]');
        if (gridElements.length > 0) {
            console.log('Found AG Grid elements:', gridElements.length);
            populateExistingGrid();
        }
    }

    async function populateExistingGrid() {
        try {
            const assessments = await window.skillsAPI.list();
            console.log('Populating grid with assessments:', assessments);
            
            // Try to find Angular component and update its data
            if (window.ng && window.ng.getComponent) {
                const gridElement = document.querySelector('[class*="ag-grid"]');
                if (gridElement) {
                    const component = window.ng.getComponent(gridElement);
                    if (component && component.rowData) {
                        component.rowData = assessments;
                        if (component.gridApi) {
                            component.gridApi.setRowData(assessments);
                        }
                    }
                }
            }
            
            // Alternative: Try to find gridApi globally
            if (window.gridApi) {
                window.gridApi.setRowData(assessments);
            }
            
            // Another approach: dispatch custom event
            window.dispatchEvent(new CustomEvent('skillsDataLoaded', { detail: assessments }));
            
        } catch (error) {
            console.error('Error populating existing grid:', error);
        }
    }

    // Make functions globally available
    window.loadAssessmentsList = loadAssessmentsList;
    window.deleteAssessmentItem = deleteAssessmentItem;
    window.populateExistingGrid = populateExistingGrid;
})();