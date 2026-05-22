import { useState } from 'react'
import { classifySystem, downloadReport } from '../api/client'
import RiskBadge from '../components/RiskBadge'

const SECTORS = [
  'healthcare', 'employment', 'education', 'law_enforcement',
  'border_control', 'critical_infrastructure', 'justice', 'finance', 'other'
]

export default function Classify() {
  const [version, setVersion] = useState('v1') // V1 vs V2 switch state!
  const [language, setLanguage] = useState('en') // German, French, Spanish flags state!
  
  const [form, setForm] = useState({
    system_name: '',
    description: '',
    intended_purpose: '', // New V2 attribute!
    sector: 'healthcare',
    automated_decision: false,
    processes_personal_data: false,
    interacts_with_humans: false,
  })
  
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState(null)

  const set = (field, value) => setForm(f => ({ ...f, [field]: value }))

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const payload = { ...form }
      // If client orders from Window 1 (V1), strip off V2 healthy attributes!
      if (version === 'v1') {
        delete payload.intended_purpose
      }
      
      const res = await classifySystem(payload, version)
      setResult(res.data)
    } catch (e) {
      const detail = e.response?.data?.detail
      const msg = typeof detail === 'string' 
        ? detail 
        : (Array.isArray(detail) ? detail[0]?.msg : 'Classification failed')
      setError(msg || 'Classification failed')
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
        language: language // On-the-fly flag selection passed to ReportLab!
      })
    } catch (e) {
      setError('Report download failed')
    } finally {
      setDownloading(false)
    }
  }

  const inputStyle = {
    width: '100%',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    padding: '10px 14px',
    color: 'var(--text-primary)',
    fontFamily: 'IBM Plex Sans, sans-serif',
    fontSize: '14px',
    outline: 'none',
    transition: 'border-color 0.15s ease',
  }

  const labelStyle = {
    display: 'block',
    fontFamily: 'IBM Plex Mono, monospace',
    fontSize: '11px',
    color: 'var(--text-secondary)',
    letterSpacing: '0.08em',
    marginBottom: '6px',
  }

  return (
    <div style={{ animation: 'slideUp 0.4s ease forwards' }}>
      <div style={{ marginBottom: '32px' }}>
        <div style={{
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '11px',
          color: 'var(--accent)',
          letterSpacing: '0.12em',
          marginBottom: '8px',
        }}>
          EU AI ACT COMPLIANCE PORTAL
        </div>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 700,
          fontFamily: 'Inter, sans-serif',
          color: 'var(--text-primary)',
          letterSpacing: '-0.02em',
          marginBottom: '8px',
        }}>
          Risk Classification
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          Classify an AI system into its EU AI Act risk tier and generate compliance obligations.
        </p>
      </div>

      {/* Feynman Cafeteria Version Selector Switch */}
      <div style={{
        display: 'flex',
        background: 'var(--bg-elevated)',
        border: '1px solid var(--border)',
        borderRadius: '12px',
        padding: '6px',
        marginBottom: '28px',
        gap: '8px',
      }}>
        {[
          { id: 'v1', name: 'Window 1: Legacy V1 Engine', desc: 'GDPR, Risk Tiers, and Scanners' },
          { id: 'v2', name: 'Window 2: Regulated V2 Act', desc: 'EU AI Act 2024 with Intended Purpose' }
        ].map(opt => (
          <button
            key={opt.id}
            onClick={() => {
              setVersion(opt.id)
              setResult(null)
              setError(null)
            }}
            style={{
              flex: 1,
              padding: '12px',
              background: version === opt.id ? 'var(--accent)' : 'transparent',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              textAlign: 'center',
            }}
          >
            <div style={{
              fontSize: '13px',
              fontWeight: 600,
              color: version === opt.id ? 'var(--bg-base)' : 'var(--text-primary)',
              fontFamily: 'Inter, sans-serif'
            }}>{opt.name}</div>
            <div style={{
              fontSize: '10px',
              color: version === opt.id ? 'rgba(0,0,0,0.6)' : 'var(--text-muted)',
              fontFamily: 'IBM Plex Mono, monospace',
              marginTop: '2px'
            }}>{opt.desc}</div>
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border)',
          borderRadius: '12px',
          padding: '28px',
        }}>
          <div style={{
            fontSize: '14px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            marginBottom: '24px',
            fontFamily: 'Inter, sans-serif',
          }}>
            System Details
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>SYSTEM NAME</label>
            <input
              style={inputStyle}
              value={form.system_name}
              onChange={e => set('system_name', e.target.value)}
              placeholder="e.g. Patient Diagnosis Assistant"
              onFocus={e => e.target.style.borderColor = 'var(--accent)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>DESCRIPTION</label>
            <textarea
              style={{ ...inputStyle, height: '100px', resize: 'vertical' }}
              value={form.description}
              onChange={e => set('description', e.target.value)}
              placeholder="Describe what the AI system does..."
              onFocus={e => e.target.style.borderColor = 'var(--accent)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
          </div>

          {/* Slide down Intended Purpose field if in Window 2 (V2) */}
          {version === 'v2' && (
            <div style={{ marginBottom: '20px', animation: 'slideUp 0.3s ease forwards' }}>
              <label style={{ ...labelStyle, color: 'var(--accent)' }}>INTENDED PURPOSE (MANDATORY IN V2)</label>
              <textarea
                style={{ ...inputStyle, height: '80px', resize: 'vertical', borderColor: 'var(--accent)' }}
                value={form.intended_purpose}
                onChange={e => set('intended_purpose', e.target.value)}
                placeholder="Specify the exact clinical/industrial goals (e.g. to assist ICU radiologists in crisis)..."
                onFocus={e => e.target.style.borderColor = 'var(--accent)'}
                onBlur={e => e.target.style.borderColor = 'var(--accent)'}
              />
            </div>
          )}

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

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '28px' }}>
            {[
              { field: 'automated_decision', label: 'Makes automated decisions without human review' },
              { field: 'processes_personal_data', label: 'Processes personal data of individuals' },
              { field: 'interacts_with_humans', label: 'Directly interacts with humans' },
            ].map(({ field, label }) => (
              <label key={field} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                cursor: 'pointer',
                padding: '10px 14px',
                background: form[field] ? 'var(--accent-dim)' : 'var(--bg-elevated)',
                border: `1px solid ${form[field] ? 'var(--accent)' : 'var(--border)'}`,
                borderRadius: '8px',
                transition: 'all 0.15s ease',
              }}>
                <input
                  type="checkbox"
                  checked={form[field]}
                  onChange={e => set(field, e.target.checked)}
                  style={{ width: '16px', height: '16px', accentColor: 'var(--accent)', flexShrink: 0 }}
                />
                <span style={{ fontSize: '13px', color: 'var(--text-primary)' }}>{label}</span>
              </label>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading || !form.system_name || !form.description || (version === 'v2' && !form.intended_purpose)}
            style={{
              width: '100%',
              padding: '13px',
              background: loading || !form.system_name || !form.description || (version === 'v2' && !form.intended_purpose)
                ? 'var(--bg-elevated)'
                : 'var(--accent)',
              color: loading || !form.system_name || !form.description || (version === 'v2' && !form.intended_purpose)
                ? 'var(--text-muted)'
                : 'var(--bg-base)',
              border: 'none',
              borderRadius: '8px',
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '12px',
              fontWeight: 600,
              letterSpacing: '0.08em',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {loading ? 'CLASSIFYING...' : 'CLASSIFY SYSTEM →'}
          </button>

          {error && (
            <div style={{
              marginTop: '12px',
              padding: '12px 14px',
              background: 'rgba(248,81,73,0.08)',
              border: '1px solid var(--danger)',
              borderRadius: '8px',
              fontSize: '13px',
              color: 'var(--danger)',
            }}>
              {error}
            </div>
          )}
        </div>

        <div>
          {!result && !loading && (
            <div style={{
              height: '100%',
              minHeight: '300px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px dashed var(--border)',
              borderRadius: '12px',
              color: 'var(--text-muted)',
              gap: '12px',
            }}>
              <div style={{ fontSize: '32px', opacity: 0.3 }}>⬡</div>
              <div style={{
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '12px',
                color: 'var(--text-muted)',
              }}>
                Results will appear here
              </div>
            </div>
          )}

          {result && (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              animation: 'slideUp 0.3s ease forwards',
            }}>
              <div style={{
                background: 'var(--bg-surface)',
                border: '1px solid var(--border)',
                borderRadius: '12px',
                padding: '24px',
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '16px',
                }}>
                  <div>
                    <div style={{
                      fontFamily: 'IBM Plex Mono, monospace',
                      fontSize: '10px',
                      color: 'var(--text-secondary)',
                      letterSpacing: '0.08em',
                      marginBottom: '4px',
                    }}>
                      CLASSIFICATION RESULT {version.toUpperCase()}
                    </div>
                    <div style={{
                      fontSize: '20px',
                      fontWeight: 700,
                      fontFamily: 'Inter, sans-serif',
                      color: 'var(--text-primary)',
                      letterSpacing: '-0.01em',
                    }}>
                      {result.system_name}
                    </div>
                  </div>
                  <RiskBadge tier={result.risk_tier} />
                </div>
                
                {/* Visual framework indicator stamp */}
                <div style={{
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '10px',
                  color: 'var(--accent)',
                  fontWeight: 600,
                  marginBottom: '12px',
                }}>
                  FRAMEWORK: {result.regulatory_framework || 'EU AI Act (Proposed)'}
                </div>

                <p style={{
                  fontSize: '13px',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.7,
                  marginBottom: '16px',
                }}>
                  {result.justification}
                </p>
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  background: result.dpia_required
                    ? 'rgba(248,81,73,0.08)'
                    : 'rgba(63,185,80,0.08)',
                  border: `1px solid ${result.dpia_required ? 'var(--danger)' : 'var(--success)'}`,
                  borderRadius: '6px',
                }}>
                  <div style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    background: result.dpia_required ? 'var(--danger)' : 'var(--success)',
                  }} />
                  <span style={{
                    fontFamily: 'IBM Plex Mono, monospace',
                    fontSize: '11px',
                    color: result.dpia_required ? 'var(--danger)' : 'var(--success)',
                    fontWeight: 600,
                  }}>
                    DPIA {result.dpia_required ? 'REQUIRED' : 'NOT REQUIRED'}
                  </span>
                </div>
              </div>

              <div style={{
                background: 'var(--bg-surface)',
                border: '1px solid var(--border)',
                borderRadius: '12px',
                padding: '24px',
              }}>
                <div style={{
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '11px',
                  color: 'var(--text-secondary)',
                  letterSpacing: '0.08em',
                  marginBottom: '16px',
                }}>
                  COMPLIANCE OBLIGATIONS ({result.obligations.length})
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {result.obligations.map((ob, i) => (
                    <div key={i} style={{
                      display: 'flex',
                      gap: '12px',
                      padding: '8px 0',
                      borderBottom: i < result.obligations.length - 1
                        ? '1px solid var(--border)'
                        : 'none',
                      fontSize: '13px',
                      color: 'var(--text-secondary)',
                      lineHeight: 1.5,
                    }}>
                      <span style={{
                        fontFamily: 'IBM Plex Mono, monospace',
                        fontSize: '11px',
                        color: 'var(--accent)',
                        flexShrink: 0,
                        marginTop: '1px',
                      }}>
                        {String(i + 1).padStart(2, '0')}
                      </span>
                      {ob}
                    </div>
                  ))}
                </div>
              </div>

              {/* Dynamic Flag / Language Selector */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                padding: '10px 14px',
              }}>
                <label style={{
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '11px',
                  color: 'var(--text-secondary)',
                  margin: 0,
                  flexGrow: 1
                }}>COMPLIANCE REPORT LANGUAGE</label>
                <select
                  value={language}
                  onChange={e => setLanguage(e.target.value)}
                  style={{
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border)',
                    borderRadius: '6px',
                    color: 'var(--text-primary)',
                    padding: '6px 12px',
                    fontSize: '13px',
                    cursor: 'pointer',
                    outline: 'none'
                  }}
                >
                  <option value="en">🇬🇧 English</option>
                  <option value="de">🇩🇪 Deutsch</option>
                  <option value="fr">🇫🇷 Français</option>
                  <option value="es">🇪🇸 Español</option>
                </select>
              </div>

              <button
                onClick={handleDownload}
                disabled={downloading}
                style={{
                  width: '100%',
                  padding: '13px',
                  background: 'transparent',
                  color: 'var(--accent)',
                  border: '1px solid var(--accent)',
                  borderRadius: '8px',
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '12px',
                  fontWeight: 600,
                  letterSpacing: '0.08em',
                  cursor: downloading ? 'not-allowed' : 'pointer',
                  opacity: downloading ? 0.5 : 1,
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={e => {
                  if (!downloading) {
                    e.target.style.background = 'var(--accent-dim)'
                  }
                }}
                onMouseLeave={e => {
                  e.target.style.background = 'transparent'
                }}
              >
                {downloading ? 'GENERATING PDF...' : '↓ DOWNLOAD COMPLIANCE REPORT'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
