// API Base URL
// Prefer global config set by embed.js or host page, fallback to current origin
let API_BASE_URL = (window.RagChatbotConfig && window.RagChatbotConfig.apiUrl) || window.location.origin;

// Expose minimal API to allow runtime override from embed loader
window.ChatbotWidget = window.ChatbotWidget || {
    setApiUrl: function(url) {
        if (typeof url === 'string' && url.length > 0) {
            API_BASE_URL = url;
            console.log('[ChatbotWidget] API base set to:', API_BASE_URL);
        }
    },
    getApiUrl: function() {
        return API_BASE_URL;
    }
};

// Session ID for conversation continuity
let sessionId = `user-${Date.now()}`;

// Chat history
let chatHistory = [];

// Widget State
let isWidgetOpen = false;
let isWidgetMinimized = false;

// DOM Elements - Declare but initialize after DOM loads
let chatBubble, chatWidget, closeWidgetBtn, minimizeWidgetBtn;
let chatTab, chatContent;
let chatMessages, messageInput, sendBtn;
let docCount, chatCount;

// Counters
let documentsIngested = 0;
let messagesSent = 0;

// Initialize function
function initializeWidget() {
    console.log('[ChatbotWidget] Initializing...');
    
    // Initialize all DOM elements
    chatBubble = document.getElementById('chatBubble');
    chatWidget = document.getElementById('chatWidget');
    closeWidgetBtn = document.getElementById('closeWidget');
    minimizeWidgetBtn = document.getElementById('minimizeWidget');
    chatTab = document.getElementById('chatTab');
    chatContent = document.getElementById('chatContent');
    chatMessages = document.getElementById('chatMessages');
    messageInput = document.getElementById('messageInput');
    sendBtn = document.getElementById('sendBtn');
    docCount = document.getElementById('docCount');
    chatCount = document.getElementById('chatCount');
    
    if (!chatBubble || !chatWidget) {
        console.warn('[ChatbotWidget] Elements not found, retrying...');
        return false;
    }
    
    // Now setup everything
    setupEventListeners();
    setupWidgetListeners();
    setupResizeHandlers();
    setupDragHandler();
    autoResizeTextarea();
    
    // Initialize widget state from localStorage
    const savedState = localStorage.getItem('widgetState');
    if (savedState === 'open') {
        openWidget();
    }
    
    console.log('[ChatbotWidget] Initialized successfully');
    return true;
}

// Initialize when DOM is ready or immediately if already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeWidget);
} else {
    // DOM already loaded (script loaded dynamically), try to initialize
    setTimeout(initializeWidget, 100);
}

// Expose initialize function for embed loader
window.ChatbotWidget = window.ChatbotWidget || {};
window.ChatbotWidget.init = initializeWidget;
window.ChatbotWidget.setApiUrl = function(url) {
    if (typeof url === 'string' && url.length > 0) {
        API_BASE_URL = url;
        console.log('[ChatbotWidget] API base set to:', API_BASE_URL);
    }
};
window.ChatbotWidget.getApiUrl = function() {
    return API_BASE_URL;
};

// Widget Functions
function setupWidgetListeners() {
    console.log('Setting up widget listeners...');
    console.log('chatBubble:', chatBubble);
    console.log('chatWidget:', chatWidget);
    
    if (!chatBubble || !chatWidget) {
        console.error('Widget elements not found!');
        return;
    }
    
    // Open widget when bubble is clicked
    chatBubble.addEventListener('click', () => {
        console.log('Bubble clicked!');
        if (isWidgetOpen) {
            if (isWidgetMinimized) {
                maximizeWidget();
            }
        } else {
            openWidget();
        }
    });
    
    // Close widget
    if (closeWidgetBtn) {
        closeWidgetBtn.addEventListener('click', closeWidget);
    }
    
    // Minimize widget
    if (minimizeWidgetBtn) {
        minimizeWidgetBtn.addEventListener('click', minimizeWidget);
    }
    
    // Tab switching - removed, only chat tab remains
}

function openWidget() {
    console.log('Opening widget...');
    chatWidget.style.display = 'flex';
    chatBubble.style.display = 'none';
    isWidgetOpen = true;
    isWidgetMinimized = false;
    localStorage.setItem('widgetState', 'open');
    
    // Focus on message input
    setTimeout(() => {
        if (messageInput) {
            messageInput.focus();
        }
    }, 300);
}

function closeWidget() {
    chatWidget.style.display = 'none';
    chatBubble.style.display = 'flex';
    isWidgetOpen = false;
    isWidgetMinimized = false;
    localStorage.setItem('widgetState', 'closed');
}

function minimizeWidget() {
    chatWidget.classList.add('minimized');
    isWidgetMinimized = true;
}

function maximizeWidget() {
    chatWidget.classList.remove('minimized');
    isWidgetMinimized = false;
}

// Widget Resize Functionality
function setupResizeHandlers() {
    const resizeHandles = document.querySelectorAll('.resize-handle');
    let isResizing = false;
    let currentHandle = null;
    let startX, startY, startWidth, startHeight, startLeft, startBottom;

    resizeHandles.forEach(handle => {
        handle.addEventListener('mousedown', (e) => {
            isResizing = true;
            currentHandle = handle;
            startX = e.clientX;
            startY = e.clientY;
            
            const rect = chatWidget.getBoundingClientRect();
            startWidth = rect.width;
            startHeight = rect.height;
            startLeft = window.innerWidth - rect.right;
            startBottom = window.innerHeight - rect.bottom;
            
            e.preventDefault();
        });
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing || !currentHandle) return;

        const dx = e.clientX - startX;
        const dy = e.clientY - startY;

        const minWidth = 320;
        const minHeight = 400;
        const maxWidth = window.innerWidth - 40;
        const maxHeight = window.innerHeight - 120;

        if (currentHandle.classList.contains('resize-right')) {
            const newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth + dx));
            chatWidget.style.width = newWidth + 'px';
        }
        
        if (currentHandle.classList.contains('resize-left')) {
            const newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth - dx));
            chatWidget.style.width = newWidth + 'px';
            chatWidget.style.right = (startLeft - dx) + 'px';
        }
        
        if (currentHandle.classList.contains('resize-bottom')) {
            const newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight + dy));
            chatWidget.style.height = newHeight + 'px';
        }
        
        if (currentHandle.classList.contains('resize-top')) {
            const newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight - dy));
            chatWidget.style.height = newHeight + 'px';
            chatWidget.style.bottom = (startBottom + dy) + 'px';
        }

        // Corner handles
        if (currentHandle.classList.contains('resize-bottom-right')) {
            const newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth + dx));
            const newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight + dy));
            chatWidget.style.width = newWidth + 'px';
            chatWidget.style.height = newHeight + 'px';
        }

        if (currentHandle.classList.contains('resize-bottom-left')) {
            const newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth - dx));
            const newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight + dy));
            chatWidget.style.width = newWidth + 'px';
            chatWidget.style.height = newHeight + 'px';
            chatWidget.style.right = (startLeft - dx) + 'px';
        }

        if (currentHandle.classList.contains('resize-top-right')) {
            const newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth + dx));
            const newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight - dy));
            chatWidget.style.width = newWidth + 'px';
            chatWidget.style.height = newHeight + 'px';
            chatWidget.style.bottom = (startBottom + dy) + 'px';
        }

        if (currentHandle.classList.contains('resize-top-left')) {
            const newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth - dx));
            const newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight - dy));
            chatWidget.style.width = newWidth + 'px';
            chatWidget.style.height = newHeight + 'px';
            chatWidget.style.right = (startLeft - dx) + 'px';
            chatWidget.style.bottom = (startBottom + dy) + 'px';
        }
    });

    document.addEventListener('mouseup', () => {
        isResizing = false;
        currentHandle = null;
    });
}

// Setup drag to move functionality
function setupDragHandler() {
    const widgetHeader = document.querySelector('.widget-header');
    const chatWidget = document.getElementById('chatWidget');
    let isDragging = false;
    let startX, startY;
    let startLeft, startTop;

    widgetHeader.addEventListener('mousedown', (e) => {
        // Don't drag if clicking on buttons
        if (e.target.closest('.widget-controls') || e.target.closest('button')) {
            return;
        }

        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        
        const rect = chatWidget.getBoundingClientRect();
        startLeft = rect.left;
        startTop = rect.top;
        
        // Change cursor
        widgetHeader.style.cursor = 'grabbing';
        
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;

        const dx = e.clientX - startX;
        const dy = e.clientY - startY;

        let newLeft = startLeft + dx;
        let newTop = startTop + dy;

        // Get widget dimensions
        const rect = chatWidget.getBoundingClientRect();
        const widgetWidth = rect.width;
        const widgetHeight = rect.height;

        // Constrain to viewport
        const minLeft = 0;
        const maxLeft = window.innerWidth - widgetWidth;
        const minTop = 0;
        const maxTop = window.innerHeight - widgetHeight;

        newLeft = Math.max(minLeft, Math.min(maxLeft, newLeft));
        newTop = Math.max(minTop, Math.min(maxTop, newTop));

        // Update position using top/left instead of bottom/right
        chatWidget.style.left = newLeft + 'px';
        chatWidget.style.top = newTop + 'px';
        chatWidget.style.right = 'auto';
        chatWidget.style.bottom = 'auto';
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            widgetHeader.style.cursor = 'grab';
        }
    });
}

// Setup Event Listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    messageInput.addEventListener('input', () => {
        autoResizeTextarea();
        // Enable/disable send button based on input
        sendBtn.disabled = !messageInput.value.trim();
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
    sendBtn.disabled = true;
    autoResizeTextarea();
    
    // Show typing indicator
    showTypingIndicator();
    
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
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Display bot response
        addMessage('bot', data.answer, data.sources);
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage('bot', '❌ Sorry, I encountered an error. Please make sure the API is running and documents are ingested.', []);
        showToast('Failed to get response', 'error');
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

// Show Typing Indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message message-bot typing-indicator';
    typingDiv.id = 'typing-indicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-wrapper">
            <div class="message-label">AI Assistant</div>
            <div class="message-content">
                <span class="loading"></span>
                <span style="margin-left: 8px; color: var(--text-secondary);">Thinking...</span>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove Typing Indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
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
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
            </div>
            <h2>How can I help you today?</h2>
            <p>Upload documents and ask questions to get AI-powered answers</p>
            <div class="welcome-steps">
                <div class="step">
                    <span class="step-number">1</span>
                    <span>Upload your documents or add a URL</span>
                </div>
                <div class="step">
                    <span class="step-number">2</span>
                    <span>Ask questions about your content</span>
                </div>
                <div class="step">
                    <span class="step-number">3</span>
                    <span>Get instant answers with source references</span>
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

// Show typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message message-bot typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-wrapper">
            <div class="message-label">AI Assistant</div>
            <div class="message-content" style="display: flex; align-items: center; gap: 6px;">
                <span class="loading"></span>
                <span style="color: var(--text-secondary);">Thinking...</span>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Auto-refresh health status every 30 seconds
setInterval(checkHealth, 30000);

// Debug logging
console.log('chatBubble:', chatBubble);
console.log('chatWidget:', chatWidget);
