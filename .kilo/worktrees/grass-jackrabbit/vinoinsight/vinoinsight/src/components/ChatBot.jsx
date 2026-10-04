import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { MessageCircle, X, Send, Wine, Sparkles } from 'lucide-react';
import { API_BASE } from '../context/AuthContext';
import styles from './ChatBot.module.css';

// Small instant local fallback used only if the backend request itself fails
// (e.g. backend not running) — the real answers come from /api/chat, which
// is backed by Google Gemini with its own server-side offline fallback.
function localFallback() {
  return "I couldn't reach the server just now. Make sure the backend (python app.py) is running, then try again.";
}

// Starter prompts shown before the user's first message. These deliberately
// span the GENERAL wine domain rather than the app's chemistry inputs: user
// testing showed beginners assumed the assistant only handled acidity/pH
// questions, because that was all the old placeholder text advertised.
const STARTERS = [
  'What wine should a beginner start with?',
  'What food goes with red wine?',
  'Difference between Champagne and Prosecco?',
  'How long does opened wine last?',
];

const GREETING =
  "Hi! I'm the VinoInsight wine assistant. Ask me anything about wine — grape " +
  "varieties, wine styles, taste and aroma, food pairing, serving and storage, " +
  "wine regions, how wine is made, or how this app's predictions work. No prior " +
  "wine knowledge needed.";

export default function ChatBot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    // ai: false — this is a hardcoded static greeting shown before any backend
    // call is made, not an actual model response, so it must not carry the
    // "AI-generated" badge. Real replies below use res.data.ai_powered from
    // the backend, which tests/test_chat.py verifies is false when no API key
    // is configured.
    { role: 'bot', text: GREETING, ai: false }
  ]);
  const [input, setInput] = useState('');
  const [thinking, setThinking] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, open, thinking]);

  // Shared by the form submit and the suggestion chips.
  const send = async (text) => {
    if (!text || thinking) return;

    const history = messages.map(m => ({
      role: m.role === 'bot' ? 'model' : 'user',
      text: m.text,
    }));
    setMessages(m => [...m, { role: 'user', text }]);
    setInput('');
    setThinking(true);

    try {
      const res = await axios.post(`${API_BASE}/chat`, { message: text, history });
      setMessages(m => [...m, { role: 'bot', text: res.data.answer, ai: res.data.ai_powered }]);
    } catch (err) {
      setMessages(m => [...m, { role: 'bot', text: localFallback(), ai: false }]);
    } finally {
      setThinking(false);
    }
  };

  const handleSend = (e) => {
    e.preventDefault();
    send(input.trim());
  };

  const showStarters = messages.length === 1 && !thinking;

  return (
    <>
      <button
        className={styles.fab}
        onClick={() => setOpen(o => !o)}
        aria-label="Open wine assistant chat"
      >
        {open ? <X size={22} /> : <MessageCircle size={22} />}
      </button>

      {open && (
        <div className={styles.panel}>
          <div className={styles.header}>
            <Wine size={16} />
            <span>Wine Assistant</span>
          </div>
          <div className={styles.messages}>
            {messages.map((m, i) => (
              <div key={i} className={m.role === 'bot' ? styles.botMsg : styles.userMsg}>
                {m.text}
                {m.role === 'bot' && m.ai && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 6, opacity: 0.55, fontSize: '0.68rem' }}>
                    <Sparkles size={10} /> AI-generated
                  </div>
                )}
              </div>
            ))}

            {showStarters && (
              <div className={styles.suggestions}>
                {STARTERS.map(s => (
                  <button
                    key={s}
                    type="button"
                    className={styles.suggestion}
                    onClick={() => send(s)}
                    disabled={thinking}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}

            {thinking && <div className={styles.botMsg}>Thinking…</div>}
            <div ref={endRef} />
          </div>
          <form className={styles.inputRow} onSubmit={handleSend}>
            <input
              type="text"
              placeholder="Ask anything about wine…"
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={thinking}
            />
            <button type="submit" aria-label="Send" disabled={thinking}><Send size={16} /></button>
          </form>
        </div>
      )}
    </>
  );
}
