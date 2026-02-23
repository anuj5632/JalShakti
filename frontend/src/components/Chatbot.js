import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './Chatbot.css';

const Chatbot = ({ sensorData, isOpen, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [language, setLanguage] = useState('english');
  const [isLoading, setIsLoading] = useState(false);
  const [quickReplies, setQuickReplies] = useState([]);
  const messagesEndRef = useRef(null);

  const languageLabels = {
    english: { name: 'English', flag: '🇬🇧', greeting: 'Hello! How can I help you?' },
    hindi: { name: 'हिंदी', flag: '🇮🇳', greeting: 'नमस्ते! मैं आपकी कैसे मदद कर सकता हूं?' },
    marathi: { name: 'मराठी', flag: '🇮🇳', greeting: 'नमस्कार! मी तुम्हाला कशी मदत करू शकतो?' }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      // Add welcome message when opened
      const welcomeMessage = {
        type: 'bot',
        content: languageLabels[language].greeting,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
      fetchQuickReplies(language);
    }
  }, [isOpen]);

  const fetchQuickReplies = async (lang) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/chatbot/quick-replies?language=${lang}`);
      if (response.data.success) {
        setQuickReplies(response.data.quick_replies);
      }
    } catch (error) {
      console.error('Failed to fetch quick replies:', error);
    }
  };

  const handleLanguageChange = async (newLang) => {
    setLanguage(newLang);
    const welcomeMessage = {
      type: 'bot',
      content: languageLabels[newLang].greeting,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
    fetchQuickReplies(newLang);
  };

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    // Add user message
    const userMessage = {
      type: 'user',
      content: text,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const params = new URLSearchParams({
        message: text,
        language: language
      });

      // Add sensor data if available
      if (sensorData) {
        if (sensorData.ph) params.append('ph', sensorData.ph);
        if (sensorData.tds) params.append('tds', sensorData.tds);
        if (sensorData.turbidity) params.append('turbidity', sensorData.turbidity);
        if (sensorData.temperature) params.append('temperature', sensorData.temperature);
      }

      const response = await axios.post(`http://localhost:8000/api/v1/chatbot?${params.toString()}`);
      
      if (response.data.success) {
        const botMessage = {
          type: 'bot',
          content: response.data.response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
        
        if (response.data.quick_replies) {
          setQuickReplies(response.data.quick_replies);
        }
      } else {
        throw new Error(response.data.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage = {
        type: 'bot',
        content: language === 'hindi' 
          ? 'क्षमा करें, कुछ गलत हो गया। कृपया पुनः प्रयास करें।'
          : language === 'marathi'
          ? 'क्षमस्व, काहीतरी चूक झाली. कृपया पुन्हा प्रयत्न करा.'
          : 'Sorry, something went wrong. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const handleQuickReply = (reply) => {
    sendMessage(reply);
  };

  const formatMessage = (content) => {
    // Convert markdown-style formatting to HTML
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br/>')
      .replace(/• /g, '&bull; ')
      .replace(/✅/g, '<span class="emoji-safe">✅</span>')
      .replace(/⚠️/g, '<span class="emoji-warning">⚠️</span>')
      .replace(/❌/g, '<span class="emoji-danger">❌</span>');
  };

  if (!isOpen) return null;

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <div className="chatbot-title">
          <span className="chatbot-icon">💧</span>
          <div className="chatbot-title-text">
            <h3>JalMitra</h3>
            <span className="chatbot-subtitle">
              {language === 'hindi' ? 'जल गुणवत्ता सहायक' : 
               language === 'marathi' ? 'पाणी गुणवत्ता सहाय्यक' : 
               'Water Quality Assistant'}
            </span>
          </div>
        </div>
        <div className="chatbot-controls">
          <div className="language-selector">
            {Object.entries(languageLabels).map(([lang, info]) => (
              <button
                key={lang}
                className={`lang-btn ${language === lang ? 'active' : ''}`}
                onClick={() => handleLanguageChange(lang)}
                title={info.name}
              >
                {info.flag}
              </button>
            ))}
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
      </div>

      <div className="chatbot-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type} ${msg.isError ? 'error' : ''}`}>
            {msg.type === 'bot' && (
              <div className="bot-avatar">🤖</div>
            )}
            <div className="message-content">
              <div 
                className="message-text"
                dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
              />
              <span className="message-time">
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message bot">
            <div className="bot-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {quickReplies.length > 0 && (
        <div className="quick-replies">
          {quickReplies.map((reply, index) => (
            <button
              key={index}
              className="quick-reply-btn"
              onClick={() => handleQuickReply(reply)}
            >
              {reply}
            </button>
          ))}
        </div>
      )}

      <form className="chatbot-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={
            language === 'hindi' ? 'अपना सवाल टाइप करें...' :
            language === 'marathi' ? 'तुमचा प्रश्न टाइप करा...' :
            'Type your question...'
          }
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !inputValue.trim()}>
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </form>
    </div>
  );
};

export default Chatbot;
