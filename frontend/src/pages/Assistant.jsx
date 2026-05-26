import { useState, useRef, useEffect } from 'react'
import { askQuestion } from '../api/client'
import ReactMarkdown from 'react-markdown'

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

  const coverage = [
    'Prohibited practices (Art. 5)',
    'High-risk obligations (Art. 6)',
    'GPAI duties (Art. 51-56)',
    'Transparency rules (Art. 52)',
  ]

  const panel = {
    background: 'linear-gradient(180deg, rgba(255,255,255,0.02), transparent 22%), var(--bg-glass)',
    border: '1px solid var(--border-glass)',
    borderRadius: '20px',
    boxShadow: 'var(--shadow-card)',
    backdropFilter: 'var(--blur)',
    WebkitBackdropFilter: 'var(--blur)',
  }

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
        content: e.response?.data?.detail || e.message || 'Failed to get response'
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'grid', gap: '20px', animation: 'slideUp 0.4s ease forwards', maxWidth: 1440 }}>
      <div>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '7px 12px',
          borderRadius: '999px',
          border: '1px solid var(--border)',
          background: 'rgba(76,195,255,0.08)',
          color: 'var(--accent)',
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '10px',
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          marginBottom: '14px',
        }}>
          Retrieval augmented assistant
        </div>
        <h1 style={{
          fontSize: 'clamp(30px, 4vw, 46px)',
          fontWeight: 700,
          fontFamily: 'Inter, sans-serif',
          color: 'var(--text-primary)',
          letterSpacing: '-0.04em',
          marginBottom: '8px',
        }}>
          AI Compliance Assistant
        </h1>
        <p style={{ fontSize: '15px', color: 'var(--text-secondary)', maxWidth: '72ch', lineHeight: 1.7 }}>
          Ask questions about the EU AI Act and get cited answers grounded in the regulatory corpus.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
        {[
          { label: 'Answer style', value: 'Cited and concise' },
          { label: 'Coverage', value: 'Articles, annexes, timelines' },
          { label: 'Use case', value: 'Policy and compliance Q&A' },
        ].map((item) => (
          <div key={item.label} style={{ ...panel, padding: '18px' }}>
            <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: '10px' }}>
              {item.label}
            </div>
            <div style={{ fontSize: '15px', color: 'var(--text-primary)', fontWeight: 600, lineHeight: 1.4 }}>
              {item.value}
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.6fr) minmax(300px, 0.9fr)', gap: '20px' }}>
        <div style={{ ...panel, display: 'flex', flexDirection: 'column', minHeight: '70vh', overflow: 'hidden' }}>
          <div style={{ padding: '22px 22px 0' }}>
            <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: '12px' }}>
              Suggested questions
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '10px', marginBottom: '12px' }}>
              {SUGGESTIONS.map(s => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  style={{
                    background: 'rgba(255,255,255,0.02)',
                    border: '1px solid var(--border)',
                    borderRadius: '16px',
                    padding: '14px 16px',
                    color: 'var(--text-secondary)',
                    fontSize: '13px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontFamily: 'IBM Plex Sans, sans-serif',
                    transition: 'all 0.15s ease',
                    lineHeight: 1.5,
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = 'var(--accent)'
                    e.currentTarget.style.color = 'var(--text-primary)'
                    e.currentTarget.style.background = 'rgba(76,195,255,0.08)'
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = 'var(--border)'
                    e.currentTarget.style.color = 'var(--text-secondary)'
                    e.currentTarget.style.background = 'rgba(255,255,255,0.02)'
                  }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div style={{
            flex: 1,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            padding: '0 22px 18px',
          }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
            animation: 'slideUp 0.3s ease forwards',
          }}>
            <div style={{
              maxWidth: msg.role === 'assistant' ? '90%' : '80%',
              background: msg.role === 'user'
                ? 'var(--accent-glow)'
                : msg.role === 'error'
                  ? 'rgba(248,81,73,0.08)'
                  : 'rgba(255,255,255,0.02)',
              border: `1px solid ${
                msg.role === 'user'
                  ? 'var(--accent)'
                  : msg.role === 'error'
                    ? 'var(--danger)'
                    : 'var(--border)'
              }`,
              borderRadius: msg.role === 'user'
                ? '20px 20px 6px 20px'
                : '20px 20px 20px 6px',
              padding: '20px',
              boxShadow: 'var(--shadow-card)',
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '12px',
                borderBottom: msg.role !== 'user' ? '1px solid rgba(255,255,255,0.05)' : 'none',
                paddingBottom: msg.role !== 'user' ? '12px' : '0',
              }}>
                <div style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '6px',
                  background: msg.role === 'user' ? 'var(--accent)' : msg.role === 'error' ? 'var(--danger)' : 'var(--border-bright)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: msg.role === 'user' ? '#fff' : 'var(--bg-base)',
                  fontSize: '12px',
                  fontWeight: 'bold',
                  fontFamily: 'Inter, sans-serif'
                }}>
                  {msg.role === 'user' ? 'U' : msg.role === 'error' ? '!' : 'AI'}
                </div>
                <div style={{
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '11px',
                  color: msg.role === 'user' ? 'var(--accent)' : 'var(--text-secondary)',
                  letterSpacing: '0.14em',
                  textTransform: 'uppercase',
                  fontWeight: 600
                }}>
                  {msg.role === 'user' ? 'You' : msg.role === 'error' ? 'Error' : 'Compliance Assistant'}
                </div>
              </div>
              
              <div className="markdown-body" style={{
                fontSize: '14px',
                color: 'var(--text-primary)',
              }}>
                {msg.role === 'user' ? (
                  <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>{msg.content}</div>
                ) : (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                )}
              </div>
              {msg.sources && (
                <div style={{
                  marginTop: '12px',
                  paddingTop: '12px',
                  borderTop: '1px solid var(--border)',
                }}>
                  <div style={{
                    fontFamily: 'IBM Plex Mono, monospace',
                    fontSize: '10px',
                    color: 'var(--text-secondary)',
                    letterSpacing: '0.08em',
                    marginBottom: '8px',
                  }}>
                    SOURCES
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {msg.sources.map(s => (
                      <span key={s.id} style={{
                        background: 'rgba(255,255,255,0.03)',
                        border: '1px solid var(--border)',
                        borderRadius: '999px',
                        padding: '5px 10px',
                        fontFamily: 'IBM Plex Mono, monospace',
                        fontSize: '10px',
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
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid var(--border)',
              borderRadius: '18px 18px 18px 6px',
              padding: '16px 20px',
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '12px',
              color: 'var(--text-secondary)',
            }}>
              Retrieving relevant articles...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
          </div>

          <div style={{
            padding: '16px 18px 18px',
            borderTop: '1px solid var(--border)',
            background: 'rgba(255,255,255,0.01)',
          }}>
            <div style={{
              display: 'flex',
              gap: '12px',
              padding: '14px 14px 14px 16px',
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid var(--border)',
              borderRadius: '18px',
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
                  background: loading || !input.trim() ? 'rgba(255,255,255,0.04)' : 'linear-gradient(135deg, var(--accent), rgba(76,195,255,0.7))',
                  border: 'none',
                  borderRadius: '14px',
                  padding: '10px 18px',
                  color: loading || !input.trim() ? 'var(--text-muted)' : '#07111f',
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '11px',
                  fontWeight: 700,
                  letterSpacing: '0.14em',
                  textTransform: 'uppercase',
                  cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                Send
              </button>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gap: '20px', alignContent: 'start' }}>
          <div style={{ ...panel, padding: '22px' }}>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '12px' }}>
              What it can answer
            </div>
            <div style={{ display: 'grid', gap: '10px' }}>
              {coverage.map(item => (
                <div key={item} style={{
                  padding: '12px 14px',
                  borderRadius: '14px',
                  border: '1px solid var(--border)',
                  background: 'rgba(255,255,255,0.02)',
                  color: 'var(--text-secondary)',
                  fontSize: '13px',
                  lineHeight: 1.5,
                }}>
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div style={{ ...panel, padding: '22px' }}>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '12px' }}>
              Example prompts
            </div>
            <div style={{ display: 'grid', gap: '10px' }}>
              {SUGGESTIONS.slice(0, 3).map(item => (
                <button
                  key={item}
                  onClick={() => send(item)}
                  style={{
                    border: '1px solid var(--border)',
                    background: 'rgba(255,255,255,0.02)',
                    color: 'var(--text-secondary)',
                    padding: '12px 14px',
                    borderRadius: '14px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: '13px',
                    lineHeight: 1.5,
                  }}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}