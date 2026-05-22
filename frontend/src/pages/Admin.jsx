import { useState, useEffect } from 'react'
import { 
  listRules, 
  deactivateRule, 
  verifyLedger, 
  injectTamper, 
  restoreLedger, 
  generateTraffic 
} from '../api/client'
import RiskBadge from '../components/RiskBadge'

export default function Admin() {
  const [rules, setRules] = useState([])
  const [loading, setLoading] = useState(true)
  const [includeInactive, setIncludeInactive] = useState(false)
  const [confirming, setConfirming] = useState(null)
  const [search, setSearch] = useState('')

  // Sandbox HUD state
  const [audit, setAudit] = useState(null)
  const [auditing, setAuditing] = useState(false)
  const [sandboxLoading, setSandboxLoading] = useState(false)
  const [auditError, setAuditError] = useState(null)
  const [sandboxMessage, setSandboxMessage] = useState(null)

  const fetchRules = async () => {
    setLoading(true)
    try {
      const res = await listRules(includeInactive)
      setRules(res.data)
    } finally {
      setLoading(false)
    }
  }

  const runAudit = async () => {
    setAuditing(true)
    setAuditError(null)
    try {
      const res = await verifyLedger()
      setAudit(res.data)
    } catch (e) {
      setAuditError(e.response?.data?.detail || 'Audit verification check failed')
    } finally {
      setAuditing(false)
    }
  }

  useEffect(() => {
    fetchRules()
    runAudit()
  }, [includeInactive])

  const handleDeactivate = async (id) => {
    await deactivateRule(id)
    setConfirming(null)
    fetchRules()
  }

  // Sandbox Controllers
  const triggerTraffic = async () => {
    setSandboxLoading(true)
    setSandboxMessage(null)
    try {
      const res = await generateTraffic()
      setSandboxMessage(res.data.status)
      await runAudit() // Refresh HUD!
    } catch (e) {
      setAuditError('Failed to generate mock traffic')
    } finally {
      setSandboxLoading(false)
    }
  }

  const triggerTamper = async () => {
    setSandboxLoading(true)
    setSandboxMessage(null)
    try {
      const res = await injectTamper()
      setSandboxMessage(`Tampered! Corrupted Block ID: ${res.data.corrupted_id}`)
      await runAudit() // Refresh HUD to show Red Alarm!
    } catch (e) {
      setAuditError(e.response?.data?.detail || 'Failed to inject database tamper')
    } finally {
      setSandboxLoading(false)
    }
  }

  const triggerRestore = async () => {
    setSandboxLoading(true)
    setSandboxMessage(null)
    try {
      const res = await restoreLedger()
      setSandboxMessage(res.data.status)
      await runAudit() // Refresh HUD to return to Green Shield!
    } catch (e) {
      setAuditError('Failed to self-heal database')
    } finally {
      setSandboxLoading(false)
    }
  }

  const filtered = rules.filter(r =>
    r.risk_tier.includes(search.toLowerCase()) ||
    (r.sector || '').includes(search.toLowerCase()) ||
    (r.keyword || '').includes(search.toLowerCase())
  )

  // Style helpers
  const sandboxBtnStyle = {
    flex: 1,
    padding: '10px 12px',
    borderRadius: '6px',
    border: '1px solid var(--border)',
    background: 'var(--bg-elevated)',
    color: 'var(--text-primary)',
    fontFamily: 'IBM Plex Mono, monospace',
    fontSize: '11px',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.15s ease',
  }

  return (
    <div style={{ animation: 'slideUp 0.4s ease forwards' }}>
      
      {/* 🛡️ DYNAMIC COMPLIANCE LEDGER AUDITING HUD */}
      <div style={{
        background: 'var(--bg-surface)',
        border: '2px solid var(--border)',
        borderRadius: '16px',
        padding: '24px',
        marginBottom: '32px',
        boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
        display: 'grid',
        gridTemplateColumns: '1fr 2fr',
        gap: '24px',
        alignItems: 'center',
      }}>
        
        {/* Left Side: Glowing Circular Status Shield */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '12px',
          borderRight: '1px solid var(--border)',
          textAlign: 'center',
        }}>
          {auditing ? (
            <div style={{
              width: '80px',
              height: '80px',
              borderRadius: '50%',
              border: '4px dashed var(--accent)',
              animation: 'spin 3s linear infinite',
              marginBottom: '16px',
            }} />
          ) : (auditError || (audit && !audit.is_valid)) ? (
            <div style={{
              width: '80px',
              height: '80px',
              borderRadius: '50%',
              background: 'rgba(248,81,73,0.1)',
              border: '4px solid var(--danger)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '36px',
              color: 'var(--danger)',
              boxShadow: '0 0 20px rgba(248,81,73,0.3)',
              animation: 'pulse 1.5s infinite',
              marginBottom: '16px',
            }}>
              🚨
            </div>
          ) : (
            <div style={{
              width: '80px',
              height: '80px',
              borderRadius: '50%',
              background: 'rgba(63,185,80,0.1)',
              border: '4px solid var(--success)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '36px',
              color: 'var(--success)',
              boxShadow: '0 0 20px rgba(63,185,80,0.3)',
              marginBottom: '16px',
            }}>
              🛡️
            </div>
          )}

          <div style={{
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '12px',
            fontWeight: 700,
            color: auditing ? 'var(--accent)' : (auditError || (audit && !audit.is_valid)) ? 'var(--danger)' : 'var(--success)',
          }}>
            {auditing ? 'SCANNING LEDGER...' : (auditError || (audit && !audit.is_valid)) ? 'TAMPER DETECTED!' : 'LEDGER SECURED'}
          </div>
          
          <div style={{
            fontSize: '10px',
            color: 'var(--text-muted)',
            fontFamily: 'IBM Plex Mono, monospace',
            marginTop: '4px',
          }}>
            {audit && audit.is_valid && `${audit.total_records_verified} blocks chained`}
          </div>
        </div>

        {/* Right Side: Interactive Sandbox Details & Controls */}
        <div>
          <div style={{
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '11px',
            color: 'var(--accent)',
            letterSpacing: '0.12em',
            marginBottom: '4px',
          }}>
            CRYPTOGRAPHIC AUDIT COCKPIT (SANDBOX MODE)
          </div>
          <h2 style={{
            fontSize: '20px',
            fontWeight: 700,
            fontFamily: 'Inter, sans-serif',
            color: 'var(--text-primary)',
            marginBottom: '8px',
            letterSpacing: '-0.01em',
          }}>
            Real-Time Integrity HUD
          </h2>
          
          <p style={{
            fontSize: '13px',
            color: 'var(--text-secondary)',
            lineHeight: 1.5,
            marginBottom: '16px',
          }}>
            {auditing 
              ? 'Verifying signatures, block hash links, and recalculating SHA-256 fingerprints...' 
              : (auditError || (audit && !audit.is_valid))
                ? `ALARM: ${(audit && audit.reason) || auditError}` 
                : 'Diaries are wax-sealed (RSA-2048 signed) and sequentially summary-chained (SHA-256 links). Database is fully intact.'
            }
          </p>

          {/* Controls suite */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button 
              onClick={runAudit}
              disabled={auditing || sandboxLoading}
              style={{ ...sandboxBtnStyle, borderColor: 'var(--accent)', color: 'var(--accent)' }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--accent-dim)'}
              onMouseLeave={e => e.currentTarget.style.background = 'var(--bg-elevated)'}
            >
              🔍 VERIFY LEDGER
            </button>
            <button 
              onClick={triggerTraffic}
              disabled={auditing || sandboxLoading}
              style={sandboxBtnStyle}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
            >
              ⚡ GENERATE TRAFFIC
            </button>
            <button 
              onClick={triggerTamper}
              disabled={auditing || sandboxLoading || (audit && audit.is_valid === false)}
              style={{ ...sandboxBtnStyle, color: 'var(--danger)' }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(248,81,73,0.08)'}
              onMouseLeave={e => e.currentTarget.style.background = 'var(--bg-elevated)'}
            >
              🚨 INJECT TAMPER
            </button>
            <button 
              onClick={triggerRestore}
              disabled={auditing || sandboxLoading}
              style={{ ...sandboxBtnStyle, color: 'var(--success)' }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(63,185,80,0.08)'}
              onMouseLeave={e => e.currentTarget.style.background = 'var(--bg-elevated)'}
            >
              💚 SELF-HEAL LEDGER
            </button>
          </div>

          {sandboxMessage && (
            <div style={{
              marginTop: '12px',
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '11px',
              color: 'var(--accent)',
            }}>
              ⚙️ STATUS: {sandboxMessage}
            </div>
          )}
        </div>
      </div>

      {/* --- STANDARD RULE MANAGEMENT VIEW --- */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '11px',
          color: 'var(--accent)',
          letterSpacing: '0.12em',
          marginBottom: '8px',
        }}>
          CLASSIFICATION RULES SYSTEM
        </div>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 700,
          fontFamily: 'Inter, sans-serif',
          color: 'var(--text-primary)',
          letterSpacing: '-0.02em',
          marginBottom: '8px',
        }}>
          Governance Classifier Rules
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          Manage EU AI Act classification rules. Changes take effect immediately — no deployment required.
        </p>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        marginBottom: '16px',
      }}>
        <input
          placeholder="Search rules..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{
            flex: 1,
            background: 'var(--bg-surface)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            padding: '9px 14px',
            color: 'var(--text-primary)',
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontSize: '14px',
            outline: 'none',
          }}
          onFocus={e => e.target.style.borderColor = 'var(--accent)'}
          onBlur={e => e.target.style.borderColor = 'var(--border)'}
        />
        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          cursor: 'pointer',
          padding: '9px 14px',
          background: 'var(--bg-surface)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          whiteSpace: 'nowrap',
        }}>
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={e => setIncludeInactive(e.target.checked)}
            style={{ accentColor: 'var(--accent)' }}
          />
          <span style={{
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontSize: '13px',
            color: 'var(--text-secondary)',
          }}>
            Show inactive
          </span>
        </label>
        <div style={{
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '11px',
          color: 'var(--text-secondary)',
          whiteSpace: 'nowrap',
        }}>
          {filtered.length} rules
        </div>
      </div>

      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: '12px',
        overflow: 'hidden',
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '60px 1fr 1fr 2fr 120px',
          padding: '12px 20px',
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-elevated)',
        }}>
          {['PRI', 'CONDITION', 'TIER', 'JUSTIFICATION', 'ACTION'].map(h => (
            <div key={h} style={{
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '10px',
              color: 'var(--text-secondary)',
              letterSpacing: '0.1em',
            }}>
              {h}
            </div>
          ))}
        </div>

        {loading ? (
          <div style={{
            padding: '48px',
            textAlign: 'center',
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '12px',
            color: 'var(--text-secondary)',
          }}>
            Loading rules...
          </div>
        ) : (
          filtered.map((rule, i) => (
            <div
              key={rule.id}
              style={{
                display: 'grid',
                gridTemplateColumns: '60px 1fr 1fr 2fr 120px',
                padding: '14px 20px',
                borderBottom: i < filtered.length - 1 ? '1px solid var(--border)' : 'none',
                alignItems: 'center',
                opacity: rule.is_active ? 1 : 0.4,
                transition: 'background 0.15s ease',
                animation: `slideUp 0.3s ease ${i * 0.02}s both`,
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-elevated)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <div style={{
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '20px',
                fontWeight: 700,
                color: 'var(--accent)',
                opacity: 0.6,
              }}>
                {rule.priority}
              </div>

              <div style={{
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '11px',
                color: 'var(--text-secondary)',
              }}>
                {rule.keyword
                  ? `keyword: "${rule.keyword}"`
                  : rule.sector
                    ? `sector: ${rule.sector}`
                    : rule.interacts_with_humans
                      ? 'interacts_with_humans'
                      : 'fallback'}
              </div>

              <div>
                <RiskBadge tier={rule.risk_tier} />
              </div>

              <div style={{
                fontSize: '12px',
                color: 'var(--text-secondary)',
                lineHeight: 1.5,
                paddingRight: '16px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {rule.justification_template}
              </div>

              <div>
                {rule.is_active ? (
                  confirming === rule.id ? (
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <button
                        onClick={() => handleDeactivate(rule.id)}
                        style={{
                          padding: '5px 10px',
                          background: 'rgba(248,81,73,0.1)',
                          border: '1px solid var(--danger)',
                          borderRadius: '6px',
                          color: 'var(--danger)',
                          fontFamily: 'IBM Plex Mono, monospace',
                          fontSize: '10px',
                          cursor: 'pointer',
                        }}
                      >
                        CONFIRM
                      </button>
                      <button
                        onClick={() => setConfirming(null)}
                        style={{
                          padding: '5px 10px',
                          background: 'transparent',
                          border: '1px solid var(--border)',
                          borderRadius: '6px',
                          color: 'var(--text-secondary)',
                          fontFamily: 'IBM Plex Mono, monospace',
                          fontSize: '10px',
                          cursor: 'pointer',
                        }}
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setConfirming(rule.id)}
                      style={{
                        padding: '5px 12px',
                        background: 'transparent',
                        border: '1px solid var(--border)',
                        borderRadius: '6px',
                        color: 'var(--text-secondary)',
                        fontFamily: 'IBM Plex Mono, monospace',
                        fontSize: '10px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                      onMouseEnter={e => {
                        e.currentTarget.style.borderColor = 'var(--danger)'
                        e.currentTarget.style.color = 'var(--danger)'
                      }}
                      onMouseLeave={e => {
                        e.currentTarget.style.borderColor = 'var(--border)'
                        e.currentTarget.style.color = 'var(--text-secondary)'
                      }}
                    >
                      DEACTIVATE
                    </button>
                  )
                ) : (
                  <span style={{
                    fontFamily: 'IBM Plex Mono, monospace',
                    fontSize: '10px',
                    color: 'var(--text-muted)',
                  }}>
                    INACTIVE
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}