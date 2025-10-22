// Digital Footprint Analyzer - Frontend JavaScript

const API_BASE = window.location.origin;
let currentSessionId = null;
let pollInterval = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    checkConfig();
    setupEventListeners();
});

// Check configuration
async function checkConfig() {
    try {
        const response = await fetch(`${API_BASE}/api/config/check`);
        const data = await response.json();
        
        if (data.configured) {
            document.getElementById('config-status').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Failed to check config:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('start-btn').addEventListener('click', startAnalysis);
    document.getElementById('stored-accounts-btn').addEventListener('click', showStoredAccounts);
    document.getElementById('new-analysis-btn').addEventListener('click', resetToHome);
    document.getElementById('retry-btn').addEventListener('click', startAnalysis);
    document.getElementById('close-modal-btn').addEventListener('click', closeModal);
}

// Start analysis
async function startAnalysis() {
    try {
        // Check if we need OAuth first
        const accountsResponse = await fetch(`${API_BASE}/api/accounts`);
        const accountsData = await accountsResponse.json();
        
        if (accountsData.count === 0) {
            // No stored accounts - need to authenticate first
            await startOAuthFlow();
            return;
        }
        
        // Have stored accounts - proceed with analysis
        showSection('analysis');
        showProgress();
        
        const response = await fetch(`${API_BASE}/api/analysis/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to start analysis');
        }
        
        const data = await response.json();
        currentSessionId = data.session_id;
        
        // Start polling for status
        pollStatus();
        
    } catch (error) {
        showError(error.message);
    }
}

// Start OAuth flow (for production deployment)
async function startOAuthFlow() {
    try {
        const response = await fetch(`${API_BASE}/auth/start`);
        
        if (!response.ok) {
            throw new Error('Failed to start authentication');
        }
        
        const data = await response.json();
        
        // Store session ID
        localStorage.setItem('oauth_session_id', data.session_id);
        
        // Open OAuth URL in popup or redirect
        const width = 600;
        const height = 700;
        const left = (screen.width / 2) - (width / 2);
        const top = (screen.height / 2) - (height / 2);
        
        const popup = window.open(
            data.auth_url,
            'oauth',
            `width=${width},height=${height},left=${left},top=${top},toolbar=no,location=no,status=no,menubar=no`
        );
        
        if (!popup) {
            // Popup blocked - redirect instead
            window.location.href = data.auth_url;
            return;
        }
        
        // Listen for OAuth completion
        window.addEventListener('message', handleOAuthCallback);
        
        // Poll for OAuth completion (fallback if postMessage doesn't work)
        pollOAuthStatus(data.session_id);
        
    } catch (error) {
        showError('Authentication failed: ' + error.message);
    }
}

// Handle OAuth callback message
function handleOAuthCallback(event) {
    if (event.data.type === 'oauth_success') {
        // Clean up
        window.removeEventListener('message', handleOAuthCallback);
        localStorage.removeItem('oauth_session_id');
        
        // Show success and proceed to analysis
        alert(`Successfully authenticated as ${event.data.email}!\n\nStarting analysis...`);
        
        // Start analysis automatically
        setTimeout(() => startAnalysis(), 1000);
    }
}

// Poll OAuth status (fallback)
function pollOAuthStatus(sessionId) {
    const maxAttempts = 60; // 2 minutes
    let attempts = 0;
    
    const interval = setInterval(async () => {
        attempts++;
        
        try {
            const response = await fetch(`${API_BASE}/api/analysis/status/${sessionId}`);
            const data = await response.json();
            
            if (data.status === 'authenticated') {
                clearInterval(interval);
                localStorage.removeItem('oauth_session_id');
                
                alert(`Successfully authenticated!\n\nStarting analysis...`);
                setTimeout(() => startAnalysis(), 1000);
            }
        } catch (error) {
            console.error('Error polling OAuth status:', error);
        }
        
        if (attempts >= maxAttempts) {
            clearInterval(interval);
            // OAuth polling timeout - no action needed, user can retry
        }
    }, 2000);
}

// Poll status
function pollStatus() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/analysis/status/${currentSessionId}`);
            const data = await response.json();
            
            updateProgress(data.progress, data.message);
            
            if (data.status === 'completed') {
                clearInterval(pollInterval);
                showResults(data.result);
            } else if (data.status === 'failed') {
                clearInterval(pollInterval);
                showError(data.message);
            }
            
        } catch (error) {
            clearInterval(pollInterval);
            showError('Failed to get analysis status');
        }
    }, 1000);
}

// Update progress
function updateProgress(progress, message) {
    document.getElementById('progress-bar').style.width = `${progress}%`;
    document.getElementById('progress-text').textContent = `${progress}%`;
    document.getElementById('status-message').textContent = message;
}

// Show results
function showResults(result) {
    document.getElementById('progress-container').classList.add('hidden');
    document.getElementById('results-container').classList.remove('hidden');
    
    // Set user email
    document.getElementById('user-email').textContent = result.user_email;
    
    // Set statistics
    document.getElementById('stat-total').textContent = result.statistics.total_messages.toLocaleString();
    document.getElementById('stat-threads').textContent = result.statistics.total_threads.toLocaleString();
    document.getElementById('stat-inbox').textContent = result.statistics.inbox_count.toLocaleString();
    document.getElementById('stat-sent').textContent = result.statistics.sent_count.toLocaleString();
    
    // Show sample emails
    const sampleContainer = document.getElementById('sample-emails');
    sampleContainer.innerHTML = '';
    
    result.sample_emails.forEach((email, index) => {
        const emailDiv = document.createElement('div');
        emailDiv.className = 'border-l-4 border-purple-500 pl-4 py-2';
        emailDiv.innerHTML = `
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <p class="font-semibold text-gray-800">${escapeHtml(email.subject)}</p>
                    <p class="text-sm text-gray-600 mt-1">From: ${escapeHtml(email.from)}</p>
                    <p class="text-sm text-gray-500 mt-1">${escapeHtml(email.snippet)}...</p>
                </div>
                <span class="text-xs text-gray-500 ml-4">${formatDate(email.date)}</span>
            </div>
        `;
        sampleContainer.appendChild(emailDiv);
    });
}

// Show error
function showError(message) {
    document.getElementById('progress-container').classList.add('hidden');
    document.getElementById('error-container').classList.remove('hidden');
    document.getElementById('error-message').textContent = message;
}

// Show stored accounts
async function showStoredAccounts() {
    try {
        const response = await fetch(`${API_BASE}/api/accounts`);
        const data = await response.json();
        
        const accountsList = document.getElementById('accounts-list');
        accountsList.innerHTML = '';
        
        if (data.accounts.length === 0) {
            accountsList.innerHTML = '<p class="text-gray-600">No stored accounts found. Please start a new analysis to authenticate.</p>';
        } else {
            data.accounts.forEach(email => {
                const accountBtn = document.createElement('button');
                accountBtn.className = 'w-full px-4 py-3 bg-white rounded-lg hover:bg-purple-50 text-left transition-all border border-gray-200';
                accountBtn.innerHTML = `
                    <div class="flex items-center justify-between">
                        <span class="font-semibold text-gray-800">${escapeHtml(email)}</span>
                        <i class="fas fa-chevron-right text-purple-600"></i>
                    </div>
                `;
                accountBtn.addEventListener('click', () => {
                    closeModal();
                    startAnalysisWithEmail(email);
                });
                accountsList.appendChild(accountBtn);
            });
        }
        
        document.getElementById('accounts-modal').classList.remove('hidden');
        
    } catch (error) {
        alert('Failed to load stored accounts: ' + error.message);
    }
}

// Start analysis with specific email
async function startAnalysisWithEmail(email) {
    try {
        showSection('analysis');
        showProgress();
        
        const response = await fetch(`${API_BASE}/api/analysis/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to start analysis');
        }
        
        const data = await response.json();
        currentSessionId = data.session_id;
        
        pollStatus();
        
    } catch (error) {
        showError(error.message);
    }
}

// Close modal
function closeModal() {
    document.getElementById('accounts-modal').classList.add('hidden');
}

// Show section
function showSection(section) {
    document.getElementById('hero-section').classList.add('hidden');
    document.getElementById('analysis-section').classList.add('hidden');
    
    if (section === 'hero') {
        document.getElementById('hero-section').classList.remove('hidden');
    } else if (section === 'analysis') {
        document.getElementById('analysis-section').classList.remove('hidden');
    }
}

// Show progress
function showProgress() {
    document.getElementById('progress-container').classList.remove('hidden');
    document.getElementById('results-container').classList.add('hidden');
    document.getElementById('error-container').classList.add('hidden');
    updateProgress(0, 'Initializing...');
}

// Reset to home
function resetToHome() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    currentSessionId = null;
    showSection('hero');
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Utility: Format date
function formatDate(dateStr) {
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
        });
    } catch {
        return dateStr;
    }
}

