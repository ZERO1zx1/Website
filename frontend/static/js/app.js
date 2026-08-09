/**
 * Programming Learning Intelligence Platform
 * Frontend Application
 */

// ============ STATE MANAGEMENT ============

const app = {
    user: null,
    currentProblem: null,
    currentCode: null,
    isAuthenticated: false,
    apiBaseUrl: '/api'
};

// ============ INITIALIZATION ============

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    // Check if user is authenticated
    checkAuthentication();
}

function setupEventListeners() {
    // Auth form
    document.getElementById('auth-form').addEventListener('submit', handleAuthSubmit);
    document.getElementById('toggle-auth').addEventListener('click', toggleAuthMode);
    document.getElementById('logout-btn').addEventListener('click', logout);

    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', handleNavigation);
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// ============ AUTHENTICATION ============

async function checkAuthentication() {
    try {
        const response = await fetch(`${app.apiBaseUrl}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            app.user = await response.json();
            app.isAuthenticated = true;
            showDashboard();
            loadDashboardData();
        } else {
            showAuthSection();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        showAuthSection();
    }
}

async function handleAuthSubmit(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;

    try {
        const response = await fetch(`${app.apiBaseUrl}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, role })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.token);
            app.user = data.user;
            app.isAuthenticated = true;
            showDashboard();
            loadDashboardData();
        } else {
            showAlert('Invalid credentials', 'danger');
        }
    } catch (error) {
        console.error('Login failed:', error);
        showAlert('Login failed. Please try again.', 'danger');
    }
}

function toggleAuthMode() {
    const title = document.getElementById('auth-title');
    const btnText = document.getElementById('auth-btn-text');

    if (title.textContent === 'Login') {
        title.textContent = 'Sign Up';
        btnText.textContent = 'Sign Up';
    } else {
        title.textContent = 'Login';
        btnText.textContent = 'Login';
    }
}

async function logout() {
    localStorage.removeItem('token');
    app.isAuthenticated = false;
    app.user = null;
    showAuthSection();
}

// ============ NAVIGATION ============

function handleNavigation(e) {
    e.preventDefault();
    const href = e.target.getAttribute('href');
    showSection(href.substring(1));
}

function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('[id$="-section"]').forEach(section => {
        section.classList.add('hidden');
    });

    // Show selected section
    const section = document.getElementById(`${sectionName}-section`);
    if (section) {
        section.classList.remove('hidden');

        // Load section-specific data
        switch (sectionName) {
            case 'learn':
                loadLessons();
                break;
            case 'practice':
                loadProblems();
                break;
            case 'exams':
                loadExams();
                break;
            case 'profile':
                loadProfile();
                break;
        }
    }
}

function showDashboard() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('dashboard-section').classList.remove('hidden');
    document.getElementById('user-name').textContent = app.user?.name || 'User';
}

function showAuthSection() {
    document.getElementById('dashboard-section').classList.add('hidden');
    document.getElementById('auth-section').classList.remove('hidden');
}

// ============ DASHBOARD ============

async function loadDashboardData() {
    try {
        // Load user stats
        const masteryResponse = await fetch(`${app.apiBaseUrl}/analytics/mastery/${app.user.id}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });

        if (masteryResponse.ok) {
            const masteryData = await masteryResponse.json();
            updateDashboardStats(masteryData);
        }
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

function updateDashboardStats(masteryData) {
    const mastery = masteryData.mastery || [];
    const avgMastery = mastery.length > 0
        ? (mastery.reduce((sum, m) => sum + m.mastery_score, 0) / mastery.length).toFixed(0)
        : 0;

    document.getElementById('total-skills').textContent = mastery.length;
    document.getElementById('avg-mastery').textContent = avgMastery;
}

// ============ LESSONS ============

async function loadLessons() {
    try {
        const response = await fetch(`${app.apiBaseUrl}/lessons`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });

        if (response.ok) {
            const data = await response.json();
            renderLessons(data.lessons || []);
        }
    } catch (error) {
        console.error('Failed to load lessons:', error);
    }
}

function renderLessons(lessons) {
    const container = document.getElementById('lessons-list');
    if (lessons.length === 0) {
        container.innerHTML = '<p class="text-muted">No lessons available</p>';
        return;
    }

    container.innerHTML = lessons.map(lesson => `
        <div class="card">
            <div class="card-header">${lesson.title}</div>
            <div class="card-body">
                <p>${lesson.description}</p>
                <p class="text-muted">Skills: ${lesson.skills?.join(', ') || 'N/A'}</p>
            </div>
            <div class="card-footer">
                <button onclick="startLesson(${lesson.id})" class="btn btn-primary">Start Lesson</button>
            </div>
        </div>
    `).join('');
}

// ============ PROBLEMS ============

async function loadProblems() {
    try {
        const response = await fetch(`${app.apiBaseUrl}/problems`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });

        if (response.ok) {
            const data = await response.json();
            renderProblems(data.problems || []);
        }
    } catch (error) {
        console.error('Failed to load problems:', error);
    }
}

function renderProblems(problems) {
    const container = document.getElementById('problems-list');
    if (problems.length === 0) {
        container.innerHTML = '<p class="text-muted">No problems available</p>';
        return;
    }

    container.innerHTML = problems.map(problem => `
        <div class="card">
            <div class="card-header">${problem.title}</div>
            <div class="card-body">
                <p>${problem.description.substring(0, 100)}...</p>
                <p class="text-muted">
                    <span class="badge badge-${getDifficultyClass(problem.difficulty)}">
                        ${problem.difficulty}
                    </span>
                </p>
            </div>
            <div class="card-footer">
                <button onclick="viewProblem(${problem.id})" class="btn btn-primary">Solve</button>
            </div>
        </div>
    `).join('');
}

function getDifficultyClass(difficulty) {
    const classes = {
        'easy': 'success',
        'medium': 'warning',
        'hard': 'danger'
    };
    return classes[difficulty] || 'primary';
}

async function viewProblem(problemId) {
    try {
        const response = await fetch(`${app.apiBaseUrl}/problems/${problemId}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });

        if (response.ok) {
            const data = await response.json();
            app.currentProblem = data.problem;
            displayProblemModal(data);
        }
    } catch (error) {
        console.error('Failed to load problem:', error);
    }
}

function displayProblemModal(data) {
    document.getElementById('problem-title').textContent = data.problem.title;
    document.getElementById('problem-description').textContent = data.problem.description;
    document.getElementById('problem-difficulty').textContent = data.problem.difficulty;
    document.getElementById('problem-starter-code').textContent = data.problem.starter_code;
    document.getElementById('problem-modal').classList.add('active');
}

function closeProblemModal() {
    document.getElementById('problem-modal').classList.remove('active');
}

function startProblem() {
    closeProblemModal();
    app.currentCode = app.currentProblem.starter_code;
    document.getElementById('code-editor').value = app.currentCode;
    document.getElementById('editor-title').textContent = `Solving: ${app.currentProblem.title}`;
    document.getElementById('editor-modal').classList.add('active');
}

// ============ CODE EDITOR ============

function closeEditorModal() {
    document.getElementById('editor-modal').classList.remove('active');
}

function resetCode() {
    if (app.currentProblem) {
        document.getElementById('code-editor').value = app.currentProblem.starter_code;
        showAlert('Code reset to starter template', 'info');
    }
}

async function runCode() {
    const code = document.getElementById('code-editor').value;

    try {
        const response = await fetch(`${app.apiBaseUrl}/submissions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                problem_id: app.currentProblem.id,
                code: code
            })
        });

        if (response.ok) {
            showAlert('Code submitted for evaluation', 'info');
        }
    } catch (error) {
        console.error('Failed to run code:', error);
        showAlert('Failed to run code', 'danger');
    }
}

async function submitCode() {
    const code = document.getElementById('code-editor').value;

    try {
        const response = await fetch(`${app.apiBaseUrl}/submissions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                problem_id: app.currentProblem.id,
                code: code
            })
        });

        if (response.ok) {
            const data = await response.json();
            showAlert('Code submitted successfully!', 'success');
            closeEditorModal();
        }
    } catch (error) {
        console.error('Failed to submit code:', error);
        showAlert('Failed to submit code', 'danger');
    }
}

// ============ EXAMS ============

async function loadExams() {
    // Placeholder for exam loading
    const container = document.getElementById('exams-list');
    container.innerHTML = '<p class="text-muted">No exams scheduled</p>';
}

// ============ PROFILE ============

function loadProfile() {
    if (app.user) {
        document.getElementById('profile-name').value = app.user.name || '';
        document.getElementById('profile-email').value = app.user.email || '';
        document.getElementById('profile-role').value = app.user.role || '';
    }
}

// ============ UTILITIES ============

function showAlert(message, type = 'info') {
    const container = document.getElementById('alerts-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.style.animation = 'slideIn 0.3s ease-out';

    container.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + Enter to run code
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (!document.getElementById('editor-modal').classList.contains('hidden')) {
            runCode();
        }
    }

    // Ctrl/Cmd + Shift + Enter to submit code
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'Enter') {
        if (!document.getElementById('editor-modal').classList.contains('hidden')) {
            submitCode();
        }
    }
}

// ============ EXPORT ============

window.app = app;
window.showSection = showSection;
window.viewProblem = viewProblem;
window.closeProblemModal = closeProblemModal;
window.startProblem = startProblem;
window.closeEditorModal = closeEditorModal;
window.resetCode = resetCode;
window.runCode = runCode;
window.submitCode = submitCode;
window.startLesson = () => showAlert('Feature coming soon', 'info');
