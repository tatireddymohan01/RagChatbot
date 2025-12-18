/**
 * Frontend Configuration
 * Configure the API endpoint for the RAG Chatbot
 * 
 * IMPORTANT: Update API_BASE_URL to point to your API server
 */

// API Configuration
const CONFIG = {
    // Local development (API running on same machine)
    // API_BASE_URL: 'http://localhost:8000',
    
    // Production (deployed API)
    // API_BASE_URL: 'https://your-api-domain.com',
    
    // Azure App Service
    // API_BASE_URL: 'https://your-app-name.azurewebsites.net',
    
    // Auto-detect (use same domain as frontend, useful for full-stack deployment)
    API_BASE_URL: window.location.origin,
    
    // API timeout in milliseconds
    TIMEOUT: 60000,
    
    // Enable debug logging
    DEBUG: false
};

// Validation
if (!CONFIG.API_BASE_URL) {
    console.error('API_BASE_URL is not configured!');
    alert('API endpoint not configured. Please update config.js');
}

// Debug logging
if (CONFIG.DEBUG) {
    console.log('Frontend Configuration:', CONFIG);
}
