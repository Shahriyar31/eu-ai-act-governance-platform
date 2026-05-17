import { useState, useRef, useEffect } from 'react'
import { askQuestion } from '../api/client'

const SUGGESTIONS = [
  "What obligations apply to a High Risk AI system?",
  "When is a DPIA required under GDPR Article 35?",
  "What AI practices are prohibited under Article 5?",
  "What does Article 14 require for human oversight?",
]

export default function Assistant() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (question) => {
    const q = question || input.trim()
    if (!q || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: q }])
    setLoading(true)
    try {
      const res = await askQuestion(q)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.answer,
        sources: res.data.sources
      }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: 'Failed to get response. Is the backend running?'
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 64px)' }}>
      <div style={{ marginBottom: '24px' }}>
        <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: '8px' }}>
          RAG — RETRIEVAL AUGMENTED GENERATION
        </div>
        <h1 style={{ fontSize: '28px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
          AI Compliance Assistant
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          Ask questions about the EU AI Act. Answers are grounded in regulatory text with source citations.
        </p>
      </div>

      {messages.length === 0 && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{ fontSize: '12px', fontFamily: 'IBM Plex Mono, monospace', color: 'var(--text-secondary)', marginBottom: '12px', letterSpacing: '0.06em' }}>
            SUGGESTED QUESTIONS
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            {SUGGESTIONS.map(s => (
              <button
                key={s}
                onClick={() => send(s)}
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border)',
                  borderRadius: '4px',
                  padding: '12px 16px',
                  color: 'var(--text-secondary)',
                  fontSize: '13px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontFamily: 'IBM Plex Sans, sans-serif',
                  transition: 'border-color 0.15s',
                }}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border-bright)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      <div style={{
        flex: 1,
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        marginBottom: '16px',
        paddingRight: '4px',
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
          }}>
            <div style={{
              maxWidth: '80%',
              background: msg.role === 'user' ? 'var(--accent-dim)' : msg.role === 'error' ? '#1a0a0a' : 'var(--bg-surface)',
              border: `1px solid ${msg.role === 'user' ? 'var(--accent)' : msg.role === 'error' ? 'var(--danger)' : 'var(--border)'}`,
              borderRadius: '6px',
              padding: '16px',
            }}>
              <div style={{
                fontSize: '11px',
                fontFamily: 'IBM Plex Mono, monospace',
                color: msg.role === 'user' ? 'var(--accent)' : 'var(--text-secondary)',
                marginBottom: '8px',
                letterSpacing: '0.06em',
              }}>
                {msg.role === 'user' ? 'YOU' : msg.role === 'error' ? 'ERROR' : 'COMPLIANCE ASSISTANT'}
              </div>
              <div style={{
                fontSize: '13px',
                color: 'var(--text-primary)',
                lineHeight: 1.7,
                whiteSpace: 'pre-wrap',
              }}>
                {msg.content}
              </div>
              {msg.sources && (
                <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '11px', fontFamily: 'IBM Plex Mono, monospace', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    SOURCES
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {msg.sources.map(s => (
                      <span key={s.id} style={{
                        background: 'var(--bg-elevated)',
                        border: '1px solid var(--border)',
                        borderRadius: '3px',
                        padding: '2px 8px',
                        fontSize: '11px',
                        fontFamily: 'IBM Plex Mono, monospace',
                        color: 'var(--text-secondary)',
                      }}>
                        {s.title}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', alignItems: 'flex-start' }}>
            <div style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              padding: '16px 20px',
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '13px',
              color: 'var(--text-secondary)',
            }}>
              Retrieving relevant articles...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div style={{
        display: 'flex',
        gap: '12px',
        padding: '16px',
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: '6px',
      }}>
        <input
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: 'var(--text-primary)',
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontSize: '14px',
          }}
          placeholder="Ask about EU AI Act compliance..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          disabled={loading}
        />
        <button
          onClick={() => send()}
          disabled={loading || !input.trim()}
          style={{
            background: 'var(--accent)',
            border: 'none',
            borderRadius: '4px',
            padding: '8px 16px',
            color: '#000',
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '12px',
            fontWeight: 600,
            cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
            opacity: loading || !input.trim() ? 0.5 : 1,
          }}
        >
          SEND →
        </button>
      </div>
    </div>
  )
}