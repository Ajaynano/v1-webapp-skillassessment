class SkillsAPI {
    constructor() {
        this.apiUrl = 'https://68sje39s3m.execute-api.us-east-1.amazonaws.com/Prod/skills-assessments';
    }

    async request(operation, data = {}) {
        const payload = { operation, ...data };
        console.log('API Request:', {
            url: this.apiUrl,
            method: 'POST',
            payload: payload
        });
        
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
            
            console.log('API Response Status:', response.status);
            const result = await response.json();
            console.log('API Response Data:', result);
            
            return result;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async list() {
        return this.request('list');
    }

    async read(id) {
        return this.request('read', { SkillAssessmentId: id });
    }

    async create(assessment) {
        return this.request('create', assessment);
    }

    async update(assessment) {
        return this.request('update', assessment);
    }

    async delete(id) {
        return this.request('delete', { SkillAssessmentId: id });
    }
}

// Initialize API instance
const skillsAPI = new SkillsAPI();

// Example usage functions
async function loadSkillsAssessments() {
    try {
        const assessments = await skillsAPI.list();
        displayAssessments(assessments);
    } catch (error) {
        console.error('Failed to load assessments:', error);
    }
}

function displayAssessments(assessments) {
    const container = document.getElementById('assessments-container');
    if (!container) return;

    container.innerHTML = assessments.map(assessment => `
        <div class="assessment-card">
            <h3>${assessment.Employee}</h3>
            <p><strong>Skill:</strong> ${assessment.Skill}</p>
            <p><strong>Current:</strong> ${assessment.Current}/10</p>
            <p><strong>Target:</strong> ${assessment.Target}/10</p>
            <button onclick="editAssessment('${assessment.SkillAssessmentId}')">Edit</button>
            <button onclick="deleteAssessment('${assessment.SkillAssessmentId}')">Delete</button>
        </div>
    `).join('');
}

async function createAssessment(formData) {
    try {
        await skillsAPI.create(formData);
        loadSkillsAssessments();
    } catch (error) {
        console.error('Failed to create assessment:', error);
    }
}

async function deleteAssessment(id) {
    if (confirm('Are you sure you want to delete this assessment?')) {
        try {
            await skillsAPI.delete(id);
            loadSkillsAssessments();
        } catch (error) {
            console.error('Failed to delete assessment:', error);
        }
    }
}

// Make API available globally
window.skillsAPI = skillsAPI;
window.loadSkillsAssessments = loadSkillsAssessments;
window.createAssessment = createAssessment;
window.deleteAssessment = deleteAssessment;