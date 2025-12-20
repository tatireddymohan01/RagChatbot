// API Base URL
const API_BASE_URL = window.location.origin;

// Session ID for conversation continuity
let sessionId = `user-${Date.now()}`;

// Chat history
let chatHistory = [];

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadStatus = document.getElementById('uploadStatus');
const urlInput = document.getElementById('urlInput');
const ingestUrlBtn = document.getElementById('ingestUrlBtn');
const urlStatus = document.getElementById('urlStatus');
const systemStatus = document.getElementById('systemStatus');
const fileLabel = document.getElementById('fileLabel');
const docCount = document.getElementById('docCount');
const chatCount = document.getElementById('chatCount');

// Counters
let documentsIngested = 0;
let messagesSent = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEventListeners();
    autoResizeTextarea();
});

// Setup Event Listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    messageInput.addEventListener('input', autoResizeTextarea);
    
    clearBtn.addEventListener('click', clearChat);
    uploadBtn.addEventListener('click', uploadDocuments);
    ingestUrlBtn.addEventListener('click', ingestUrl);
    
    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            fileLabel.textContent = files.length === 1 ? files[0].name : `${files.length} files selected`;
        } else {
            fileLabel.textContent = 'Choose files';
        }
    });
}

// Auto-resize textarea
function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + 'px';
}

// Check API Health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        systemStatus.innerHTML = `
            <p><strong>Status:</strong> <span style="color: var(--success-color); display: inline-flex; align-items: center; gap: 4px;"><span style="width: 8px; height: 8px; background: var(--success-color); border-radius: 50%; display: inline-block;"></span> Online</span></p>
            <p><strong>Service:</strong> <span>${data.service}</span></p>
            <p><strong>Model:</strong> <span>${data.model}</span></p>
            <p><strong>Version:</strong> <span>${data.version}</span></p>
        `;
    } catch (error) {
        systemStatus.innerHTML = `
            <p><strong>Status:</strong> <span style="color: var(--danger-color); display: inline-flex; align-items: center; gap: 4px;"><span style="width: 8px; height: 8px; background: var(--danger-color); border-radius: 50%; display: inline-block;"></span> Offline</span></p>
            <p style="margin: 0;"><span>Unable to connect to the API</span></p>
        `;
    }
}

// Update counters
function updateCounters() {
    docCount.textContent = documentsIngested;
    chatCount.textContent = messagesSent;
}

// Send Chat Message
async function sendMessage() {
    const query = messageInput.value.trim();
    
    if (!query) return;
    
    // Display user message
    addMessage('user', query);
    messageInput.value = '';
    autoResizeTextarea();
    
    // Disable send button
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<span class="loading"></span>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                session_id: sessionId,
                chat_history: chatHistory
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Add to chat history
        chatHistory.push(
            { role: 'user', content: query },
            { role: 'assistant', content: data.answer }
        );
        
        // Display bot response
        addMessage('bot', data.answer, data.sources);
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('bot', '❌ Sorry, I encountered an error. Please make sure the API is running and documents are ingested.', []);
        showToast('Failed to get response', 'error');
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerHTML = `
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
        `;
    }
}

// Add Message to Chat
function addMessage(type, content, sources = []) {
    // Remove welcome message if it exists
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Increment message counter
    if (type === 'user') {
        messagesSent++;
        updateCounters();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    
    const label = type === 'user' ? 'You' : 'AI Assistant';
    const avatar = type === 'user' ? '👤' : '🤖';
    
    let html = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-wrapper">
            <div class="message-label">${label}</div>
            <div class="message-content">${formatMessage(content)}</div>
        </div>
    `;
    
    // Sources are hidden for cleaner UI
    // Uncomment below to show sources:
    /*
    if (sources && sources.length > 0) {
        html += '<div class="message-sources"><h4>📚 Sources:</h4>';
        sources.forEach((source, index) => {
            html += `
                <div class="source-item">
                    <strong>Source ${index + 1}:</strong> ${escapeHtml(source.source)}
                    ${source.page ? ` (Page ${source.page})` : ''}
                    <div class="source-content">${escapeHtml(source.content.substring(0, 200))}...</div>
                </div>
            `;
        });
        html += '</div>';
    }
    */
    
    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format message text (preserve line breaks)
function formatMessage(text) {
    return escapeHtml(text).replace(/\n/g, '<br>');
}

// Clear Chat
function clearChat() {
    if (!confirm('Are you sure you want to clear the conversation?')) return;
    
    chatHistory = [];
    sessionId = `user-${Date.now()}`;
    messagesSent = 0;
    updateCounters();
    
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                </svg>
            </div>
            <h2>Welcome to RAG Assistant</h2>
            <p>Your intelligent document companion powered by AI</p>
            <div class="welcome-steps">
                <div class="step">
                    <span class="step-number">1</span>
                    <span>Upload documents or add a URL</span>
                </div>
                <div class="step">
                    <span class="step-number">2</span>
                    <span>Ask questions about your content</span>
                </div>
                <div class="step">
                    <span class="step-number">3</span>
                    <span>Get AI-powered answers with sources</span>
                </div>
            </div>
        </div>
    `;
    
    showToast('Conversation cleared', 'info');
}

// Upload Documents
async function uploadDocuments() {
    const files = fileInput.files;
    
    if (files.length === 0) {
        showStatus(uploadStatus, 'Please select files to upload', 'error');
        showToast('Please select files to upload', 'error');
        return;
    }
    
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="loading"></span> Uploading...';
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/ingest/docs`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            documentsIngested += data.documents_processed || files.length;
            updateCounters();
            showStatus(
                uploadStatus,
                `✅ ${data.message}\nProcessed: ${data.documents_processed} files\nChunks: ${data.chunks_created}`,
                'success'
            );
            showToast(`Successfully uploaded ${data.documents_processed} document(s)`, 'success');
            fileInput.value = '';
            fileLabel.textContent = 'Choose files';
        } else {
            showStatus(uploadStatus, `❌ Error: ${data.detail}`, 'error');
            showToast('Failed to upload documents', 'error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showStatus(uploadStatus, '❌ Failed to upload documents', 'error');
        showToast('Failed to upload documents', 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = `
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
            Upload Documents
        `;
    }
}

// Ingest URL
async function ingestUrl() {
    const url = urlInput.value.trim();
    
    if (!url) {
        showStatus(urlStatus, 'Please enter a URL', 'error');
        showToast('Please enter a URL', 'error');
        return;
    }
    
    ingestUrlBtn.disabled = true;
    ingestUrlBtn.innerHTML = '<span class="loading"></span> Ingesting...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/ingest/url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            documentsIngested++;
            updateCounters();
            showStatus(
                urlStatus,
                `✅ ${data.message}\nChunks created: ${data.chunks_created}`,
                'success'
            );
            showToast('URL content successfully ingested', 'success');
            urlInput.value = '';
        } else {
            showStatus(urlStatus, `❌ Error: ${data.detail}`, 'error');
            showToast('Failed to ingest URL', 'error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showStatus(urlStatus, '❌ Failed to ingest URL', 'error');
        showToast('Failed to ingest URL', 'error');
    } finally {
        ingestUrlBtn.disabled = false;
        ingestUrlBtn.innerHTML = `
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
            Ingest URL
        `;
    }
}

// Show Status Message
function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status ${type}`;
    element.style.display = 'block';
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show Toast Notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    toast.innerHTML = `
        <span style="font-size: 1.2em;">${icon}</span>
        <span>${escapeHtml(message)}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'toastIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Auto-refresh health status every 30 seconds
setInterval(checkHealth, 30000);
