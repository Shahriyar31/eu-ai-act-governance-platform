import { useState } from 'react'
import { classifySystem, downloadReport } from '../api/client'
import RiskBadge from '../components/RiskBadge'

const SECTORS = [
  'healthcare', 'employment', 'education', 'law_enforcement',
  'border_control', 'critical_infrastructure', 'justice', 'finance', 'other'
]

const LANGUAGES = [
  { code: 'en', label: '🇬🇧 English' },
  { code: 'de', label: '🇩🇪 Deutsch' },
  { code: 'fr', label: '🇫🇷 Français' },
  { code: 'es', label: '🇪🇸 Español' },
]

export default function Classify() {
  const [form, setForm] = useState({
    system_name: '',
    description: '',
    sector: 'healthcare',
    automated_decision: false,
    processes_personal_data: false,
    interacts_with_humans: false,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState(null)
  const [language, setLanguage] = useState('en')

  const set = (field, value) => setForm(f => ({ ...f, [field]: value }))



  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await classifySystem(form)
      setResult(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Classification failed')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    setDownloading(true)
    try {
      await downloadReport({
        system_name: form.system_name,
        description: form.description,
        sector: form.sector,
        automated_decision: form.automated_decision,
        processes_personal_data: form.processes_personal_data,
        interacts_with_humans: form.interacts_with_humans,
        uses_llm: false,
        accepts_user_input: false,
        language: language,
      })
    } catch (e) {
      setError('Report download failed')
    } finally {
      setDownloading(false)
    }
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
          marginBottom: '10px',
        }}>
          EU AI ACT · ARTICLE 6 + ANNEX III
        </div>
        <h1 style={{
          fontSize: 'clamp(30px, 4vw, 46px)',
          fontWeight: 700,
          fontFamily: 'Inter, sans-serif',
          color: 'var(--text-primary)',
          letterSpacing: '-0.04em',
          marginBottom: '8px',
        }}>
          Risk Classification
        </h1>
        <p style={{ fontSize: '15px', color: 'var(--text-secondary)', maxWidth: '70ch', lineHeight: 1.7 }}>
          Run an EU AI Act compliance check on a new system.
        </p>
      </div>



      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.12fr) minmax(300px, 0.78fr)', gap: '16px', alignItems: 'start' }}>
        <div style={{ ...panel, padding: '24px' }}>
          <div style={{
            fontSize: '14px',
            fontWeight: 700,
            color: 'var(--text-primary)',
            marginBottom: '20px',
            fontFamily: 'Inter, sans-serif',
            letterSpacing: '-0.02em',
          }}>
            System Details
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>System Name</label>
            <input
              className="premium-input"
              style={fieldBase}
              value={form.system_name}
              onChange={e => set('system_name', e.target.value)}
              placeholder="e.g. CV Screener Pro"
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
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>Sector / Application Area</label>
            <select
              className="premium-input"
              style={{ ...fieldBase, cursor: 'pointer' }}
              value={form.sector}
              onChange={e => set('sector', e.target.value)}
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
              { field: 'automated_decision', label: 'Makes Automated Decisions', sub: 'System output directly results in actions without human intervention.' },
              { field: 'processes_personal_data', label: 'Processes Personal Data', sub: 'System ingests or analyzes PII, biometrics, or sensitive personal data.' },
              { field: 'interacts_with_humans', label: 'Direct Human Interaction', sub: 'System is a chatbot, virtual assistant, or user-facing application.' },
            ].map(({ field, label }) => (
              <label key={field} className="premium-tile" data-selected={form[field]} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                cursor: 'pointer',
                padding: '16px',
                borderRadius: '8px',
                marginBottom: '12px',
              }}>
                <input
                  type="checkbox"
                  checked={form[field]}
                  onChange={e => set(field, e.target.checked)}
                  style={{ width: '16px', height: '16px', accentColor: 'var(--accent)', flexShrink: 0 }}
                />
                <div>
                  <div style={{ fontSize: '13px', color: 'var(--text-primary)', fontWeight: 600, lineHeight: 1.3 }}>
                    {label}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {({ automated_decision: 'System output directly results in actions without human intervention.', processes_personal_data: 'System ingests or analyzes PII, biometrics, or sensitive personal data.', interacts_with_humans: 'System is a chatbot, virtual assistant, or user-facing application.' }[field])}
                  </div>
                </div>
              </label>
            ))}
          </div>

          <button
            className="premium-btn"
            onClick={handleSubmit}
            disabled={loading || !form.system_name || !form.description}
            style={{
              width: '100%',
              padding: '16px',
              borderRadius: '8px',
              fontFamily: 'Inter, sans-serif',
              fontSize: '14px',
              fontWeight: 700,
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
            }}
          >
            {loading ? 'Running assessment...' : 'Run Compliance Check  →'}
          </button>

          {error && (
            <div style={{
              marginTop: '12px',
              padding: '12px 14px',
              background: 'rgba(248,81,73,0.08)',
              border: '1px solid var(--danger)',
              borderRadius: '14px',
              fontSize: '13px',
              color: 'var(--danger)',
            }}>
              {error}
            </div>
          )}
        </div>

        <div style={{ ...panel, padding: '22px', minHeight: '100%' }}>
          {!result && !loading && (
            <div style={{
              minHeight: '238px',
              padding: '18px 6px 6px',
            }}>
              <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '12px' }}>
                Assessment Process
              </div>
              <div style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '14px' }}>
                Argus AI evaluates system profiles against the latest EU AI Act articles and Annexes III/IV.
              </div>
              <ul style={{ marginLeft: '18px', color: 'var(--text-secondary)', lineHeight: 1.75, fontSize: '13px' }}>
                <li>Identifies prohibited practices</li>
                <li>Checks high-risk use cases</li>
                <li>Maps transparency obligations</li>
                <li>Generates audit trail</li>
              </ul>
            </div>
          )}

          {result && (
            <div style={{ display: 'grid', gap: '16px', animation: 'slideUp 0.3s ease forwards' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                gap: '16px',
                paddingBottom: '16px',
                borderBottom: '1px solid var(--border)',
              }}>
                <div>
                  <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: '8px' }}>
                    Classification result
                  </div>
                  <div style={{ fontSize: '22px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>
                    {result.system_name}
                  </div>
                </div>
                <RiskBadge tier={result.risk_tier} />
              </div>

              <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.75 }}>
                {result.justification}
              </p>

              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '8px 12px', borderRadius: '999px', background: result.dpia_required ? 'rgba(248,81,73,0.1)' : 'rgba(39,209,127,0.1)', border: `1px solid ${result.dpia_required ? 'var(--danger)' : 'var(--success)'}` }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '999px', background: result.dpia_required ? 'var(--danger)' : 'var(--success)' }} />
                <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', fontWeight: 700, letterSpacing: '0.12em', color: result.dpia_required ? 'var(--danger)' : 'var(--success)', textTransform: 'uppercase' }}>
                  DPIA {result.dpia_required ? 'Required' : 'Not required'}
                </span>
              </div>

              <div style={{ marginTop: '8px' }}>
                <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: '14px' }}>
                  Compliance obligations ({result.obligations.length})
                </div>
                <div style={{ display: 'grid', gap: '10px' }}>
                  {result.obligations.map((ob, i) => (
                    <div key={i} style={{
                      display: 'grid',
                      gridTemplateColumns: '28px 1fr',
                      gap: '12px',
                      padding: '14px',
                      borderRadius: '14px',
                      border: '1px solid var(--border)',
                      background: 'var(--bg-elevated)',
                    }}>
                      <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--accent)', fontWeight: 700 }}>
                        {String(i + 1).padStart(2, '0')}
                      </div>
                      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.65 }}>
                        {ob}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '6px' }}>
                <select
                  value={language}
                  onChange={e => setLanguage(e.target.value)}
                  style={{
                    minWidth: '160px',
                    background: 'rgba(255,255,255,0.02)',
                    border: '1px solid var(--border)',
                    borderRadius: '14px',
                    padding: '0 12px',
                    color: 'var(--text-primary)',
                    fontFamily: 'IBM Plex Sans, sans-serif',
                    fontSize: '13px',
                    cursor: 'pointer',
                    outline: 'none',
                    height: '46px',
                  }}
                >
                  {LANGUAGES.map(l => (
                    <option key={l.code} value={l.code}>{l.label}</option>
                  ))}
                </select>

                <button
                  onClick={handleDownload}
                  disabled={downloading}
                  style={{
                    flex: 1,
                    minWidth: '240px',
                    padding: '14px 16px',
                    background: downloading ? 'var(--bg-elevated)' : 'transparent',
                    color: 'var(--accent)',
                    border: '1px solid var(--accent)',
                    borderRadius: '14px',
                    fontFamily: 'IBM Plex Mono, monospace',
                    fontSize: '11px',
                    fontWeight: 700,
                    letterSpacing: '0.14em',
                    textTransform: 'uppercase',
                    cursor: downloading ? 'not-allowed' : 'pointer',
                    opacity: downloading ? 0.6 : 1,
                    transition: 'all 0.15s ease',
                  }}
                >
                  {downloading ? 'Generating report...' : 'Download compliance report'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}