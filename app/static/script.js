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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    clearBtn.addEventListener('click', clearChat);
    uploadBtn.addEventListener('click', uploadDocuments);
    ingestUrlBtn.addEventListener('click', ingestUrl);
}

// Check API Health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        systemStatus.innerHTML = `
            <p><strong>Status:</strong> <span style="color: #28a745;">● ${data.status}</span></p>
            <p><strong>Service:</strong> ${data.service}</p>
            <p><strong>Model:</strong> ${data.model}</p>
            <p><strong>Version:</strong> ${data.version}</p>
        `;
    } catch (error) {
        systemStatus.innerHTML = `
            <p style="color: #dc3545;"><strong>Status:</strong> ● Offline</p>
            <p>Unable to connect to the API</p>
        `;
    }
}

// Send Chat Message
async function sendMessage() {
    const query = messageInput.value.trim();
    
    if (!query) return;
    
    // Display user message
    addMessage('user', query);
    messageInput.value = '';
    
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
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
    }
}

// Add Message to Chat
function addMessage(type, content, sources = []) {
    // Remove welcome message if it exists
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    
    const label = type === 'user' ? 'You' : '🤖 Assistant';
    
    let html = `
        <div class="message-label">${label}</div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    // Add sources if available
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
    
    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Clear Chat
function clearChat() {
    chatHistory = [];
    sessionId = `user-${Date.now()}`;
    
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <h2>👋 Welcome!</h2>
            <p>Start by uploading documents or ingesting a URL, then ask me anything about them.</p>
        </div>
    `;
}

// Upload Documents
async function uploadDocuments() {
    const files = fileInput.files;
    
    if (files.length === 0) {
        showStatus(uploadStatus, 'Please select files to upload', 'error');
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
            showStatus(
                uploadStatus,
                `✅ ${data.message}\nProcessed: ${data.documents_processed} files\nChunks: ${data.chunks_created}`,
                'success'
            );
            fileInput.value = '';
        } else {
            showStatus(uploadStatus, `❌ Error: ${data.detail}`, 'error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showStatus(uploadStatus, '❌ Failed to upload documents', 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload Documents';
    }
}

// Ingest URL
async function ingestUrl() {
    const url = urlInput.value.trim();
    
    if (!url) {
        showStatus(urlStatus, 'Please enter a URL', 'error');
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
            showStatus(
                urlStatus,
                `✅ ${data.message}\nChunks created: ${data.chunks_created}`,
                'success'
            );
            urlInput.value = '';
        } else {
            showStatus(urlStatus, `❌ Error: ${data.detail}`, 'error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showStatus(urlStatus, '❌ Failed to ingest URL', 'error');
    } finally {
        ingestUrlBtn.disabled = false;
        ingestUrlBtn.textContent = 'Ingest URL';
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

// Auto-refresh health status every 30 seconds
setInterval(checkHealth, 30000);
