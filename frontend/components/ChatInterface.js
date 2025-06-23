import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import styles from '../styles/ChatInterface.module.css';

const markdownComponents = {
  h1: ({node, ...props}) => <h1 style={{fontSize: '1.08rem', fontWeight: 'bold', margin: '0.5em 0'}} {...props} />,
  h2: ({node, ...props}) => <h2 style={{fontSize: '1.08rem', fontWeight: 'bold', margin: '0.5em 0'}} {...props} />,
  h3: ({node, ...props}) => <h3 style={{fontSize: '1.08rem', fontWeight: 'bold', margin: '0.5em 0'}} {...props} />,
  ul: ({node, ...props}) => <ul style={{listStyleType: 'none', paddingLeft: 0, margin: 0}} {...props} />,
  ol: ({node, ...props}) => <ol style={{listStyleType: 'none', paddingLeft: 0, margin: 0}} {...props} />,
  li: ({node, ...props}) => <li style={{fontSize: '1.08rem', marginBottom: '0.3em'}} {...props} />,
  strong: ({node, ...props}) => <strong style={{fontSize: '1.08rem', color: '#333'}} {...props} />,
  p: ({node, ...props}) => <p style={{fontSize: '1.08rem', margin: '0.3em 0'}} {...props} />,
};

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Update conversation history with the new user message
      const updatedHistory = [...conversationHistory, { role: 'user', content: inputMessage }];
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          history: updatedHistory
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, botMessage]);
      setConversationHistory(data.history || updatedHistory);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setConversationHistory([]);
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        {/* Welcome content */}
      </header>
      <main className={styles.main}>
        <div className={styles.chatContainer}>
          <div className={styles.chatHeader}>
            <h2>Airline Customer Service</h2>
            <button onClick={clearChat} className={styles.clearBtn}>
              Clear Chat
            </button>
          </div>
          
          <div className={styles.messagesContainer}>
            {messages.length === 0 && (
              <div className={styles.welcomeMessage}>
                <p>👋 Hello! I'm your AI assistant. How can I help you today?</p>
                <p>I can help you with:</p>
                <ul>
                  <li>📅 Flight bookings and schedules</li>
                  <li>🌤️ Weather information for your destination</li>
                  <li>❓ General travel questions</li>
                  <li>📋 Booking management</li>
                </ul>
              </div>
            )}
            
            {messages.map((message) => (
              <div
                key={message.id}
                className={`${styles.message} ${message.sender === 'user' ? styles.userMessage : styles.botMessage}`}
              >
                <div className={styles.messageContent}>
                  {message.sender === 'bot' ? (
                    <ReactMarkdown components={markdownComponents}>{message.text}</ReactMarkdown>
                  ) : (
                    <p style={{fontSize: '1.08rem', margin: '0.3em 0'}}>{message.text}</p>
                  )}
                  <span className={styles.timestamp}>{message.timestamp}</span>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className={`${styles.message} ${styles.botMessage}`}>
                <div className={styles.messageContent}>
                  <div className={styles.typingIndicator}>
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          <div className={styles.inputContainer}>
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here... (e.g., 'I need a flight from LA to NY on June 15th')"
              disabled={isLoading}
              rows={3}
              className={styles.textarea}
            />
            <button 
              onClick={sendMessage} 
              disabled={isLoading || !inputMessage.trim()}
              className={styles.sendBtn}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </main>
      <footer className={styles.footer}>
        {/* Footer content */}
      </footer>
    </div>
  );
};

export default ChatInterface; 