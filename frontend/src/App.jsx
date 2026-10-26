import React, { useState, useRef, useEffect } from 'react';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [level, setLevel] = useState('UG');
  const [subject, setSubject] = useState('Physics');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, level, subject }),
      });
      const data = await response.json();
      const botMsg = { role: 'bot', data };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error('Error fetching chat response:', error);
      const errorMsg = { role: 'bot', data: { teachingContent: "Sorry, I couldn't reach the backend server. Is it running?" } };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <aside className="glass-panel sidebar">
        <h1>AI Tutor</h1>
        
        <div className="settings-group">
          <label htmlFor="level">Academic Level</label>
          <select id="level" value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value="PUC">Pre-University (PUC)</option>
            <option value="UG">Undergraduate (UG)</option>
            <option value="PG">Postgraduate (PG)</option>
          </select>
        </div>

        <div className="settings-group">
          <label htmlFor="subject">Subject Context</label>
          <input 
            type="text" 
            id="subject" 
            value={subject} 
            onChange={(e) => setSubject(e.target.value)} 
            placeholder="e.g. Physics, History..." 
          />
        </div>
      </aside>

      <main className="glass-panel chat-area">
        <div className="chat-history">
          {messages.length === 0 && (
            <div className="message bot">
              <p>Hello! I am your AI Academic Tutor. Feel free to ask me any question.</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              {msg.role === 'user' ? (
                <p>{msg.content}</p>
              ) : (
                <>
                  {msg.data.reasoning && (
                    <div className="reasoning">
                      <strong>Reasoning:</strong> {msg.data.reasoning}
                    </div>
                  )}
                  <div className="teaching-content">
                    {msg.data.teachingContent}
                  </div>
                  {msg.data.practice && (
                    <div className="practice">
                      <strong>Practice:</strong> {msg.data.practice}
                    </div>
                  )}
                </>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="message bot typing-indicator">
              <span></span><span></span><span></span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <form className="input-container" onSubmit={handleSend}>
          <input 
            type="text" 
            value={input} 
            onChange={(e) => setInput(e.target.value)} 
            placeholder={`Ask a question for ${level} level...`}
            disabled={isLoading}
          />
          <button type="submit" className="send-btn" disabled={isLoading}>
            Send
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;
