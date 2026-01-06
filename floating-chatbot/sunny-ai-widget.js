/**
 * Sunny AI - Floating Chatbot Widget
 * Tata Capital Agentic AI Loan Assistant
 */

(function() {
    'use strict';

    // Default configuration
    const defaultConfig = {
        apiUrl: 'http://localhost:8000',
        position: 'bottom-right',
        theme: 'tata-capital',
        autoOpen: false,
        welcomeMessage: 'Hi! I\'m Sunny AI. How can I help you with your loan needs today?',
        botName: 'Sunny AI',
        companyName: 'Tata Capital'
    };

    let config = {};
    let isOpen = false;
    let websocket = null;
    let sessionId = null;
    let messageHistory = [];

    // Generate unique session ID
    function generateSessionId() {
        return 'sunny_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    // Create widget HTML st