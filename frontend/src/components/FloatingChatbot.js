import React, { useState, useEffect } from 'react';
import './FloatingChatbot.css';

const FloatingChatbot = ({ onOpenChat }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    // Show the chatbot after a delay (like Tata Capital does)
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  const handleChatClick = () => {
    if (onOpenChat) {
      onOpenChat();
    } else {
      // Default behavior - redirect to chat page
      window.open('http://localhost:3001', '_blank');
    }
  };

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const closeChatbot = () => {
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="floating-chatbot">
      {/* Collapsed Chat Button */}
      <div className={`chat-button ${isExpanded ? 'hidden' : 'visible'}`}>
        <button 
          className="chat-btn animated-btn"
          onClick={toggleExpanded}
          aria-label="Open SunnyAI"
        >
          <span className="chat-icon">💬</span>
          <span className="chat-text">SunnyAI</span>
        </button>
      </div>

      {/* Expanded Chat Widget */}
      <div className={`chat-widget ${isExpanded ? 'visible' : 'hidden'}`}>
        <div className="chat-widget-content">
          <button 
            className="close-btn"
            onClick={closeChatbot}
            aria-label="Close Chat"
          >
            ×
          </button>
          
          <div className="chat-avatar">
            <div className="avatar-image">
              <span className="avatar-icon">🤖</span>
            </div>
          </div>
          
          <div className="chat-info">
            <h3>Hi! I'm Sanhith</h3>
            <p>Your AI Loan Assistant</p>
            <p className="chat-description">
              Get instant loan approval in minutes! I can help you with personal loans, 
              home loans, and more.
            </p>
          </div>
          
          <button 
            className="start-chat-btn"
            onClick={handleChatClick}
          >
            <span className="btn-icon">💰</span>
            Start Loan Application
          </button>
          
          <div className="chat-features">
            <div className="feature">
              <span className="feature-icon">⚡</span>
              <span>Instant Approval</span>
            </div>
            <div className="feature">
              <span className="feature-icon">📱</span>
              <span>Minimal Documents</span>
            </div>
            <div className="feature">
              <span className="feature-icon">🏦</span>
              <span>Trusted by Millions</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FloatingChatbot;