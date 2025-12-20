/**
 * RAG Chatbot Widget - One-Line Embed Script
 * 
 * Usage: Add this single line to any website:
 * <script src="https://your-chatbot-domain.com/static/embed.js"></script>
 * 
 * No need to copy CSS or other JS files - everything loads automatically!
 */

(function() {
    'use strict';
    
    // Configuration - Auto-detect or use custom settings
    const config = window.RagChatbotConfig || {};
    const API_BASE_URL = config.apiUrl || window.location.origin;
    const WIDGET_POSITION = config.position || 'bottom-right'; // bottom-right, bottom-left, top-right, top-left
    const PRIMARY_COLOR = config.primaryColor || '#06b6d4';
    const BUBBLE_TEXT = config.bubbleText || '💬';
    const WIDGET_TITLE = config.title || 'AI Chat Assistant';
    const WELCOME_MESSAGE = config.welcomeMessage || '👋 Hello! How can I help you today?';
    
    // Prevent duplicate loading
    if (window.RagChatbotLoaded) {
        console.warn('RAG Chatbot widget already loaded');
        return;
    }
    window.RagChatbotLoaded = true;
    
    // Load CSS
    function loadCSS() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = `${API_BASE_URL}/static/widget.css`;
        document.head.appendChild(link);
    }
    
    // Create widget HTML
    function createWidget() {
        const widgetContainer = document.createElement('div');
        widgetContainer.id = 'rag-chatbot-container';
        widgetContainer.innerHTML = `
            <!-- Chat Bubble -->
            <button id="chatBubble" class="chat-bubble chat-bubble-${WIDGET_POSITION}" 
                    aria-label="Open chat" style="--primary-color: ${PRIMARY_COLOR}; position: fixed; width: 60px; height: 60px; border-radius: 50%; z-index: 9998; box-shadow: 0 10px 15px rgba(0,0,0,0.2); background: ${PRIMARY_COLOR}; color: #fff; display: flex; align-items: center; justify-content: center;">
                <span class="bubble-icon">${BUBBLE_TEXT}</span>
            </button>
            
            <!-- Chat Widget -->
            <div id="chatWidget" class="chat-widget" style="display:none;">
                <div class="widget-header">
                    <div class="widget-header-content">
                        <div class="widget-title">
                            <h3>${WIDGET_TITLE}</h3>
                            <p class="widget-subtitle"><span class="status-dot"></span>Online</p>
                        </div>
                    </div>
                    <div class="widget-controls">
                        <button id="minimizeWidget" class="widget-btn" title="Minimize">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="5" y1="12" x2="19" y2="12"/>
                            </svg>
                        </button>
                        <button id="closeWidget" class="widget-btn" title="Close">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/>
                                <line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div id="chatContent" class="widget-content active">
                    <div id="chatMessages" class="widget-messages">
                        <div class="welcome-message-compact">
                            <div class="welcome-icon-compact">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                                </svg>
                            </div>
                            <h4>👋 Hello!</h4>
                            <p>${WELCOME_MESSAGE}</p>
                        </div>
                    </div>
                    <div class="widget-input-area">
                        <div class="widget-input-wrapper">
                            <textarea id="messageInput" placeholder="Type your message..." rows="1"></textarea>
                            <button id="sendBtn" class="widget-send-btn" disabled>
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="22" y1="2" x2="11" y2="13"/>
                                    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="widget-footer">
                    <div class="widget-stats"><span id="docCount">0</span> docs  <span id="chatCount">0</span> messages</div>
                    <div class="widget-brand">Powered by <strong>RAG AI</strong></div>
                </div>
            </div>
        `;
        
        document.body.appendChild(widgetContainer);
    }
    
    // Load main widget script
    function loadWidgetScript() {
        const script = document.createElement('script');
        script.src = `${API_BASE_URL}/static/script_widget.js`;
        script.async = true;
        script.onload = function() {
            console.log('✅ RAG Chatbot widget loaded successfully');
            
            // Override API_BASE_URL in the widget script if needed
            if (window.ChatbotWidget && config.apiUrl) {
                window.ChatbotWidget.setApiUrl(config.apiUrl);
            }
            
            // Initialize the widget (handles dynamic loading)
            if (window.ChatbotWidget && window.ChatbotWidget.init) {
                setTimeout(() => window.ChatbotWidget.init(), 50);
            }
        };
        script.onerror = function() {
            console.error('❌ Failed to load RAG Chatbot widget');
        };
        document.body.appendChild(script);
    }
    
    // Position mapping
    const positionStyles = {
        'bottom-right': { bottom: '20px', right: '20px' },
        'bottom-left': { bottom: '20px', left: '20px' },
        'top-right': { top: '20px', right: '20px' },
        'top-left': { top: '20px', left: '20px' }
    };
    
    // Apply position
    function applyPosition() {
        const bubble = document.getElementById('chatBubble');
        if (bubble && positionStyles[WIDGET_POSITION]) {
            Object.assign(bubble.style, positionStyles[WIDGET_POSITION]);
        }
    }
    
    // Initialize when DOM is ready
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', loadWidget);
        } else {
            loadWidget();
        }
    }
    
    function loadWidget() {
        loadCSS();
        createWidget();
        applyPosition();
        loadWidgetScript();
    }
    
    // Start initialization
    init();
    
    // Expose API for customization
    window.RagChatbot = {
        open: function() {
            const event = new CustomEvent('ragChatbot:open');
            window.dispatchEvent(event);
        },
        close: function() {
            const event = new CustomEvent('ragChatbot:close');
            window.dispatchEvent(event);
        },
        send: function(message) {
            const event = new CustomEvent('ragChatbot:send', { detail: { message } });
            window.dispatchEvent(event);
        }
    };
    
})();
