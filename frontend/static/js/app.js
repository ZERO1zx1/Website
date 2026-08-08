/**
 * Programming Learning Platform - Frontend Application
 */

class App {
    constructor() {
        this.apiBase = '/api';
        this.token = localStorage.getItem('token');
        this.currentUser = null;
        this.init();
    }

    async init() {
        this.attachEventListeners();
        if (this.token) {
            await this.loadCurrentUser();
        } else {
            this.showLoginSection();
        }
    }

    attachEventListeners() {
        // Auth form listeners
        const loginForm = document.getElementById('login-form');
        const registerForm = document.getElementById('register-form');
        const showRegisterLink = document.getElementById('show-register');
        const showLoginLink = document.getElementById('show-login');

        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }
        if (showRegisterLink) {
            showRegisterLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showRegisterSection();
            });
        }
        if (showLoginLink) {
            showLoginLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showLoginSection();
            });
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch(`${this.apiBase}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.token = data.token;
                this.currentUser = data.user;
                localStorage.setItem('token', this.token);
                localStorage.setItem('user', JSON.stringify(this.currentUser));
                this.showDashboard();
                this.showAlert('Login successful!', 'success');
            } else {
                this.showAlert(data.error || 'Login failed', 'error');
            }
        } catch (error) {
            this.showAlert('An error occurred: ' + error.message, 'error');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const name = document.getElementById('reg-name').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;

        try {
            const response = await fetch(`${this.apiBase}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.showAlert('Registration successful! Please login.', 'success');
                this.showLoginSection();
            } else {
                this.showAlert(data.error || 'Registration failed', 'error');
            }
        } catch (error) {
            this.showAlert('An error occurred: ' + error.message, 'error');
        }
    }

    async loadCurrentUser() {
        try {
            const response = await fetch(`${this.apiBase}/auth/me`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });

            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.user;
                localStorage.setItem('user', JSON.stringify(this.currentUser));
                this.showDashboard();
            } else {
                this.logout();
            }
        } catch (error) {
            console.error('Error loading user:', error);
            this.logout();
        }
    }

    showLoginSection() {
        document.getElementById('login-section').style.display = 'block';
        document.getElementById('register-section').style.display = 'none';
        document.getElementById('dashboard-section').style.display = 'none';
        document.getElementById('user-info').innerHTML = '';
    }

    showRegisterSection() {
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('register-section').style.display = 'block';
        document.getElementById('dashboard-section').style.display = 'none';
    }

    showDashboard() {
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('register-section').style.display = 'none';
        document.getElementById('dashboard-section').style.display = 'block';

        // Update user info
        const userInfo = document.getElementById('user-info');
        userInfo.innerHTML = `
            <span>${this.currentUser.name} (${this.currentUser.role})</span>
            <button class="btn btn-secondary" onclick="app.logout()">Logout</button>
        `;

        this.loadDashboardContent();
    }

    loadDashboardContent() {
        const dashboardContent = document.getElementById('dashboard-content');
        
        let content = `
            <div class="card">
                <div class="card-header">Welcome, ${this.currentUser.name}!</div>
                <div class="card-body">
                    <p>Role: <strong>${this.currentUser.role}</strong></p>
        `;

        if (this.currentUser.role === 'student') {
            content += `
                <h3>Your Learning Journey</h3>
                <div class="dashboard-grid">
                    <div class="card">
                        <div class="card-header">📚 Learn</div>
                        <p>Guided lessons and tutorials</p>
                    </div>
                    <div class="card">
                        <div class="card-header">💻 Practice</div>
                        <p>Solve practice problems</p>
                    </div>
                    <div class="card">
                        <div class="card-header">📝 Assignments</div>
                        <p>Complete assignments</p>
                    </div>
                    <div class="card">
                        <div class="card-header">🏆 Exams</div>
                        <p>Take assessments</p>
                    </div>
                </div>
            `;
        } else if (this.currentUser.role === 'teacher') {
            content += `
                <h3>Teacher Dashboard</h3>
                <div class="dashboard-grid">
                    <div class="card">
                        <div class="card-header">📚 Courses</div>
                        <p>Manage your courses</p>
                    </div>
                    <div class="card">
                        <div class="card-header">👥 Students</div>
                        <p>Monitor student progress</p>
                    </div>
                    <div class="card">
                        <div class="card-header">📊 Analytics</div>
                        <p>View class analytics</p>
                    </div>
                    <div class="card">
                        <div class="card-header">🔧 Problem Bank</div>
                        <p>Create and manage problems</p>
                    </div>
                </div>
            `;
        } else if (this.currentUser.role === 'admin') {
            content += `
                <h3>Admin Dashboard</h3>
                <div class="dashboard-grid">
                    <div class="card">
                        <div class="card-header">👥 Users</div>
                        <p>Manage users and roles</p>
                    </div>
                    <div class="card">
                        <div class="card-header">✅ Approvals</div>
                        <p>Approve teacher requests</p>
                    </div>
                    <div class="card">
                        <div class="card-header">📊 System Stats</div>
                        <p>View system statistics</p>
                    </div>
                    <div class="card">
                        <div class="card-header">🔐 Security</div>
                        <p>Manage security settings</p>
                    </div>
                </div>
            `;
        }

        content += `
                </div>
            </div>
        `;

        dashboardContent.innerHTML = content;
    }

    logout() {
        this.token = null;
        this.currentUser = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        this.showLoginSection();
        this.showAlert('Logged out successfully', 'success');
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        const container = document.getElementById('main-content');
        container.insertBefore(alertDiv, container.firstChild);

        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
