import { useState } from 'react'
import api from '../api/client'
import RiskBadge from '../components/RiskBadge'

const SECTORS = [
  'healthcare', 'employment', 'education', 'law_enforcement',
  'border_control', 'critical_infrastructure', 'justice', 'finance', 'other'
]

const STEPS = [
  { key: 'classify', label: 'Risk Classification' },
  { key: 'dpia', label: 'DPIA Assessment' },
  { key: 'owasp', label: 'OWASP LLM Check' },
  { key: 'summary', label: 'Final Report' },
]

export default function Agent() {
  const [form, setForm] = useState({
    system_name: '',
    description: '',
    sector: 'healthcare',
    automated_decision: false,
    processes_personal_data: false,
    interacts_with_humans: false,
    uses_llm: false,
    accepts_user_input: false,
  })

  const [phase, setPhase] = useState('idle')
  const [threadId, setThreadId] = useState(null)
  const [clarification, setClarification] = useState(null)
  const [answers, setAnswers] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [resumeLoading, setResumeLoading] = useState(false)

  const set = (field, value) => setForm(f => ({ ...f, [field]: value }))

  const handleSubmit = async () => {
    if (!form.system_name || !form.description) return
    setPhase('loading')
    setError(null)
    setResult(null)
    setClarification(null)
    setAnswers('')
    try {
      const res = await api.post('/api/v1/agent/assess', form)
      if (res.data.status === 'awaiting_clarification') {
        setThreadId(res.data.thread_id)
        setClarification({
          risk_tier: res.data.risk_tier,
          justification: res.data.classification_justification,
          questions: res.data.questions,
        })
        setPhase('clarify')
      } else {
        setResult(res.data)
        setPhase('result')
      }
    } catch (e) {
      setError(e.response?.data?.detail || 'Assessment failed')
      setPhase('error')
    }
  }

  const handleResume = async () => {
    if (!answers.trim()) return
    setResumeLoading(true)
    setError(null)
    try {
      const res = await api.post('/api/v1/agent/assess/respond', {
        thread_id: threadId,
        answers,
      })
      setResult(res.data)
      setPhase('result')
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to resume assessment')
      setPhase('error')
    } finally {
      setResumeLoading(false)
    }
  }

  const handleReset = () => {
    setPhase('idle')
    setResult(null)
    setClarification(null)
    setThreadId(null)
    setAnswers('')
    setError(null)
  }

  const panel = {
    background: 'var(--bg-surface)',
    border: '1px solid var(--border)',
    borderRadius: '12px',
    boxShadow: 'var(--shadow-card)',
  }

  const fieldBase = {
    width: '100%',
    borderRadius: '8px',
    padding: '14px 16px',
    color: 'var(--text-primary)',
    fontFamily: 'Inter, sans-serif',
    fontSize: '15px',
  }

  const labelStyle = {
    display: 'block',
    fontFamily: 'IBM Plex Mono, monospace',
    fontSize: '10px',
    color: 'var(--text-secondary)',
    letterSpacing: '0.14em',
    marginBottom: '8px',
    textTransform: 'uppercase',
  }

  return (
    <div style={{ animation: 'slideUp 0.4s ease forwards', maxWidth: 1440, paddingBottom: '24px' }}>
      <div style={{ marginBottom: '18px' }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '8px',
          padding: '7px 12px', borderRadius: '999px',
          border: '1px solid var(--border)', background: 'rgba(76,195,255,0.08)',
          color: 'var(--accent)', fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '10px', letterSpacing: '0.16em', textTransform: 'uppercase', marginBottom: '10px',
        }}>
          LANGGRAPH · HUMAN-IN-THE-LOOP
        </div>
        <h1 style={{
          fontSize: 'clamp(30px, 4vw, 46px)', fontWeight: 700,
          fontFamily: 'Inter, sans-serif', color: 'var(--text-primary)',
          letterSpacing: '-0.04em', marginBottom: '8px',
        }}>
          Compliance Agent
        </h1>
        <p style={{ fontSize: '15px', color: 'var(--text-secondary)', maxWidth: '70ch', lineHeight: 1.7 }}>
          Multi-step LangGraph agent with human oversight. For high-risk systems, the agent pauses and asks clarifying questions before proceeding.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.12fr) minmax(300px, 0.88fr)', gap: '16px', alignItems: 'start' }}>
        <div style={{ ...panel, padding: '24px' }}>
          <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '20px', fontFamily: 'Inter, sans-serif', letterSpacing: '-0.02em' }}>
            System Details
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>System Name</label>
            <input
              className="premium-input" style={fieldBase}
              value={form.system_name}
              onChange={e => set('system_name', e.target.value)}
              placeholder="e.g. CV Screener Pro"
              disabled={phase === 'loading' || phase === 'clarify'}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>System Description</label>
            <textarea
              className="premium-input"
              style={{ ...fieldBase, height: '120px', resize: 'vertical' }}
              value={form.description}
              onChange={e => set('description', e.target.value)}
              placeholder="Describe what the AI system does, its inputs, and its outputs..."
              disabled={phase === 'loading' || phase === 'clarify'}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>Sector</label>
            <select
              className="premium-input"
              style={{ ...fieldBase, cursor: 'pointer' }}
              value={form.sector}
              onChange={e => set('sector', e.target.value)}
              disabled={phase === 'loading' || phase === 'clarify'}
            >
              {SECTORS.map(s => (
                <option key={s} value={s} style={{ background: 'var(--bg-base)' }}>
                  {s.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>

          <div style={{ borderTop: '1px solid var(--border)', paddingTop: '20px', marginBottom: '18px' }}>
            <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
              Capabilities
            </div>
            {[
              { field: 'automated_decision', label: 'Makes Automated Decisions', sub: 'Output directly results in actions without human intervention.' },
              { field: 'processes_personal_data', label: 'Processes Personal Data', sub: 'Ingests or analyzes PII, biometrics, or sensitive personal data.' },
              { field: 'interacts_with_humans', label: 'Direct Human Interaction', sub: 'Chatbot, virtual assistant, or user-facing application.' },
              { field: 'uses_llm', label: 'Uses a Language Model', sub: 'Powered by GPT, Claude, Llama, or similar LLM.' },
              { field: 'accepts_user_input', label: 'Accepts Free-Text Input', sub: 'Users can type arbitrary text into the system.' },
            ].map(({ field, label, sub }) => (
              <label key={field} className="premium-tile" data-selected={form[field]} style={{
                display: 'flex', alignItems: 'center', gap: '14px',
                cursor: phase === 'loading' || phase === 'clarify' ? 'not-allowed' : 'pointer',
                padding: '16px', borderRadius: '8px', marginBottom: '12px',
                opacity: phase === 'loading' || phase === 'clarify' ? 0.6 : 1,
              }}>
                <input
                  type="checkbox" checked={form[field]}
                  onChange={e => set(field, e.target.checked)}
                  disabled={phase === 'loading' || phase === 'clarify'}
                  style={{ width: '16px', height: '16px', accentColor: 'var(--accent)', flexShrink: 0 }}
                />
                <div>
                  <div style={{ fontSize: '13px', color: 'var(--text-primary)', fontWeight: 600, lineHeight: 1.3 }}>{label}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>{sub}</div>
                </div>
              </label>
            ))}
          </div>

          {phase !== 'clarify' && phase !== 'result' && (
            <button
              className="premium-btn"
              onClick={handleSubmit}
              disabled={phase === 'loading' || !form.system_name || !form.description}
              style={{
                width: '100%', padding: '16px', borderRadius: '8px',
                fontFamily: 'Inter, sans-serif', fontSize: '14px',
                fontWeight: 700, letterSpacing: '0.04em', textTransform: 'uppercase',
              }}
            >
              {phase === 'loading' ? 'Agent running...' : 'Run Compliance Agent →'}
            </button>
          )}

          {(phase === 'result' || phase === 'error') && (
            <button
              className="premium-btn"
              onClick={handleReset}
              style={{
                width: '100%', padding: '16px', borderRadius: '8px',
                fontFamily: 'Inter, sans-serif', fontSize: '14px',
                fontWeight: 700, letterSpacing: '0.04em', textTransform: 'uppercase',
                background: 'transparent', color: 'var(--accent)', border: '1px solid var(--accent)',
              }}
            >
              New Assessment
            </button>
          )}

          {error && (
            <div style={{
              marginTop: '12px', padding: '12px 14px',
              background: 'rgba(248,81,73,0.08)', border: '1px solid var(--danger)',
              borderRadius: '14px', fontSize: '13px', color: 'var(--danger)',
            }}>
              {error}
            </div>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ ...panel, padding: '22px' }}>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '16px' }}>
              Agent Pipeline
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {STEPS.map((step, i) => {
                const completed = result && result.steps_completed && result.steps_completed.some(s => s.toLowerCase().includes(step.key))
                const active = phase === 'loading'
                return (
                  <div key={step.key} style={{
                    display: 'flex', alignItems: 'center', gap: '12px',
                    padding: '10px 14px', borderRadius: '8px',
                    background: completed ? 'rgba(39,209,127,0.06)' : active ? 'rgba(76,195,255,0.04)' : 'var(--bg-elevated)',
                    border: `1px solid ${completed ? 'var(--success)' : active ? 'var(--border-bright)' : 'var(--border)'}`,
                    transition: 'all 0.3s ease',
                  }}>
                    <div style={{
                      width: '22px', height: '22px', borderRadius: '50%', flexShrink: 0,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: completed ? 'var(--success)' : 'var(--bg-base)',
                      border: `1px solid ${completed ? 'var(--success)' : 'var(--border)'}`,
                      fontSize: '11px', color: completed ? 'var(--bg-base)' : 'var(--text-muted)',
                      fontFamily: 'IBM Plex Mono, monospace',
                    }}>
                      {completed ? '✓' : String(i + 1).padStart(2, '0')}
                    </div>
                    <span style={{
                      fontSize: '13px', fontWeight: completed ? 600 : 400,
                      color: completed ? 'var(--success)' : 'var(--text-secondary)',
                    }}>
                      {step.label}
                    </span>
                    {phase === 'clarify' && step.key === 'classify' && (
                      <span style={{
                        marginLeft: 'auto', fontFamily: 'IBM Plex Mono, monospace',
                        fontSize: '9px', color: 'var(--accent)', letterSpacing: '0.1em',
                      }}>
                        PAUSED
                      </span>
                    )}
                  </div>
                )
              })}
            </div>
          </div>

          {phase === 'idle' && (
            <div style={{ ...panel, padding: '22px' }}>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '12px' }}>
                How it works
              </div>
              <ul style={{ margin: 0, paddingLeft: '18px', color: 'var(--text-secondary)', lineHeight: 1.8, fontSize: '13px' }}>
                <li>Agent classifies the system risk tier</li>
                <li>For HIGH/LIMITED risk — pauses and asks questions</li>
                <li>You answer, agent resumes with full context</li>
                <li>Generates DPIA, OWASP check, and final report</li>
              </ul>
            </div>
          )}

          {phase === 'loading' && (
            <div style={{ ...panel, padding: '22px', textAlign: 'center' }}>
              <div style={{
                width: '40px', height: '40px', borderRadius: '50%',
                border: '3px solid var(--border)', borderTopColor: 'var(--accent)',
                animation: 'spin 0.8s linear infinite', margin: '0 auto 16px',
              }} />
              <div style={{ fontSize: '14px', color: 'var(--text-primary)', fontWeight: 600, marginBottom: '6px' }}>
                Agent running...
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontFamily: 'IBM Plex Mono, monospace' }}>
                Classifying system against EU AI Act
              </div>
            </div>
          )}

          {phase === 'clarify' && clarification && (
            <div style={{ ...panel, padding: '22px' }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px',
                padding: '12px 16px', borderRadius: '8px',
                background: 'rgba(210,153,34,0.08)', border: '1px solid var(--warning)',
              }}>
                <div style={{ fontSize: '18px' }}>⚠️</div>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--warning)', marginBottom: '2px' }}>
                    Human Review Required
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)', fontFamily: 'IBM Plex Mono, monospace' }}>
                    Agent paused — awaiting your input
                  </div>
                </div>
                <div style={{ marginLeft: 'auto' }}>
                  <RiskBadge tier={clarification.risk_tier} />
                </div>
              </div>

              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: '16px', padding: '12px', background: 'var(--bg-elevated)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                {clarification.justification}
              </div>

              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '10px', fontFamily: 'IBM Plex Mono, monospace', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                  Clarifying Questions
                </div>
                {clarification.questions.map((q, i) => (
                  <div key={i} style={{
                    display: 'flex', gap: '10px', marginBottom: '8px',
                    padding: '10px 14px', background: 'var(--bg-elevated)',
                    border: '1px solid var(--border)', borderRadius: '8px',
                  }}>
                    <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--accent)', fontWeight: 700, flexShrink: 0, marginTop: '1px' }}>
                      Q{i + 1}
                    </span>
                    <span style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.55 }}>{q}</span>
                  </div>
                ))}
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{
                  display: 'block', fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '10px', color: 'var(--text-secondary)',
                  letterSpacing: '0.14em', marginBottom: '8px', textTransform: 'uppercase',
                }}>Your Answers</label>
                <textarea
                  className="premium-input"
                  style={{ ...fieldBase, height: '100px', resize: 'vertical' }}
                  value={answers}
                  onChange={e => setAnswers(e.target.value)}
                  placeholder="Answer the questions above to help the agent complete the assessment..."
                />
              </div>

              <button
                className="premium-btn"
                onClick={handleResume}
                disabled={resumeLoading || !answers.trim()}
                style={{
                  width: '100%', padding: '14px', borderRadius: '8px',
                  fontFamily: 'Inter, sans-serif', fontSize: '14px',
                  fontWeight: 700, letterSpacing: '0.04em', textTransform: 'uppercase',
                }}
              >
                {resumeLoading ? 'Agent resuming...' : 'Submit Answers & Continue →'}
              </button>
            </div>
          )}

          {phase === 'result' && result && (
            <div style={{ ...panel, padding: '22px', display: 'grid', gap: '16px', animation: 'slideUp 0.3s ease forwards' }}>
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
                gap: '16px', paddingBottom: '16px', borderBottom: '1px solid var(--border)',
              }}>
                <div>
                  <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Final Report
                  </div>
                  <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>
                    {result.system_name}
                  </div>
                </div>
                <RiskBadge tier={result.risk_tier} />
              </div>

              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.75, margin: 0 }}>
                {result.final_summary}
              </p>

              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: '8px',
                padding: '8px 12px', borderRadius: '999px',
                background: result.dpia_required ? 'rgba(248,81,73,0.1)' : 'rgba(39,209,127,0.1)',
                border: `1px solid ${result.dpia_required ? 'var(--danger)' : 'var(--success)'}`,
              }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '999px', background: result.dpia_required ? 'var(--danger)' : 'var(--success)' }} />
                <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', fontWeight: 700, letterSpacing: '0.12em', color: result.dpia_required ? 'var(--danger)' : 'var(--success)', textTransform: 'uppercase' }}>
                  DPIA {result.dpia_required ? 'Required' : 'Not Required'}
                </span>
              </div>

              {result.steps_completed?.length > 0 && (
                <div>
                  <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: '10px' }}>
                    Completed Steps
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {result.steps_completed.map((step, i) => (
                      <span key={i} style={{
                        padding: '4px 10px', borderRadius: '999px',
                        background: 'rgba(39,209,127,0.08)', border: '1px solid var(--success)',
                        fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--success)',
                      }}>
                        ✓ {step}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      <style dangerouslySetInnerHTML={{__html: '@keyframes spin { to { transform: rotate(360deg) } }'}} />
    </div>
  )
}
