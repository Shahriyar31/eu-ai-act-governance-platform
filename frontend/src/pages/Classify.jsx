import { useState } from 'react'
import { classifySystem } from '../api/client'
import RiskBadge from '../components/RiskBadge'

const SECTORS = [
  'healthcare', 'employment', 'education', 'law_enforcement',
  'border_control', 'critical_infrastructure', 'justice', 'finance', 'other'
]

const inputStyle = {
  width: '100%',
  background: 'var(--bg-elevated)',
  border: '1px solid var(--border)',
  borderRadius: '4px',
  padding: '10px 12px',
  color: 'var(--text-primary)',
  fontFamily: 'IBM Plex Sans, sans-serif',
  fontSize: '13px',
  outline: 'none',
}

const labelStyle = {
  display: 'block',
  fontSize: '12px',
  fontFamily: 'IBM Plex Mono, monospace',
  color: 'var(--text-secondary)',
  letterSpacing: '0.06em',
  marginBottom: '6px',
}

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
  const [error, setError] = useState(null)

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

  const set = (field, value) => setForm(f => ({ ...f, [field]: value }))

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: '8px' }}>
          EU AI ACT — ARTICLE 6 & ANNEX III
        </div>
        <h1 style={{ fontSize: '28px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
          Risk Classification
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          Classify an AI system into its EU AI Act risk tier and generate compliance obligations.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '6px', padding: '28px' }}>
          <h2 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '24px' }}>
            System Details
          </h2>

          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>SYSTEM NAME</label>
            <input
              style={inputStyle}
              value={form.system_name}
              onChange={e => set('system_name', e.target.value)}
              placeholder="e.g. Patient Diagnosis Assistant"
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>DESCRIPTION</label>
            <textarea
              style={{ ...inputStyle, height: '100px', resize: 'vertical' }}
              value={form.description}
              onChange={e => set('description', e.target.value)}
              placeholder="Describe what the AI system does..."
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>SECTOR</label>
            <select
              style={{ ...inputStyle, cursor: 'pointer' }}
              value={form.sector}
              onChange={e => set('sector', e.target.value)}
            >
              {SECTORS.map(s => (
                <option key={s} value={s} style={{ background: 'var(--bg-surface)' }}>
                  {s.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '28px' }}>
            {[
              { field: 'automated_decision', label: 'Makes automated decisions without human review' },
              { field: 'processes_personal_data', label: 'Processes personal data of individuals' },
              { field: 'interacts_with_humans', label: 'Directly interacts with humans' },
            ].map(({ field, label }) => (
              <label key={field} style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={form[field]}
                  onChange={e => set(field, e.target.checked)}
                  style={{ width: '16px', height: '16px', accentColor: 'var(--accent)' }}
                />
                <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{label}</span>
              </label>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading || !form.system_name || !form.description}
            style={{
              width: '100%',
              padding: '12px',
              background: loading ? 'var(--bg-elevated)' : 'var(--accent)',
              color: loading ? 'var(--text-secondary)' : '#000',
              border: 'none',
              borderRadius: '4px',
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '12px',
              fontWeight: 600,
              letterSpacing: '0.08em',
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'CLASSIFYING...' : 'CLASSIFY SYSTEM →'}
          </button>

          {error && (
            <div style={{ marginTop: '12px', padding: '10px', background: '#1a0a0a', border: '1px solid var(--danger)', borderRadius: '4px', fontSize: '13px', color: 'var(--danger)' }}>
              {error}
            </div>
          )}
        </div>

        <div>
          {!result && !loading && (
            <div style={{
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px dashed var(--border)',
              borderRadius: '6px',
              color: 'var(--text-muted)',
              fontSize: '13px',
              fontFamily: 'IBM Plex Mono, monospace',
            }}>
              Results will appear here
            </div>
          )}

          {result && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '6px', padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                  <div>
                    <div style={{ fontSize: '11px', fontFamily: 'IBM Plex Mono, monospace', color: 'var(--text-secondary)', marginBottom: '4px' }}>CLASSIFICATION RESULT</div>
                    <div style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text-primary)' }}>{result.system_name}</div>
                  </div>
                  <RiskBadge tier={result.risk_tier} />
                </div>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                  {result.justification}
                </p>
                <div style={{ marginTop: '12px', padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: '4px', display: 'inline-block' }}>
                  <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: result.dpia_required ? 'var(--danger)' : 'var(--success)' }}>
                    DPIA {result.dpia_required ? 'REQUIRED' : 'NOT REQUIRED'}
                  </span>
                </div>
              </div>

              <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '6px', padding: '24px' }}>
                <div style={{ fontSize: '12px', fontFamily: 'IBM Plex Mono, monospace', color: 'var(--text-secondary)', marginBottom: '16px', letterSpacing: '0.06em' }}>
                  COMPLIANCE OBLIGATIONS ({result.obligations.length})
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {result.obligations.map((ob, i) => (
                    <div key={i} style={{ display: 'flex', gap: '10px', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                      <span style={{ color: 'var(--accent)', fontFamily: 'IBM Plex Mono, monospace', flexShrink: 0 }}>
                        {String(i + 1).padStart(2, '0')}
                      </span>
                      {ob}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}