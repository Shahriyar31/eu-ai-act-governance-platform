import { useState, useEffect } from 'react'
import { listRules, deactivateRule } from '../api/client'
import RiskBadge from '../components/RiskBadge'

export default function Admin() {
  const [rules, setRules] = useState([])
  const [loading, setLoading] = useState(true)
  const [includeInactive, setIncludeInactive] = useState(false)
  const [confirming, setConfirming] = useState(null)
  const [search, setSearch] = useState('')

  const fetchRules = async () => {
    setLoading(true)
    try {
      const res = await listRules(includeInactive)
      setRules(res.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchRules() }, [includeInactive])

  const handleDeactivate = async (id) => {
    await deactivateRule(id)
    setConfirming(null)
    fetchRules()
  }

  const filtered = rules.filter(r =>
    r.risk_tier.includes(search.toLowerCase()) ||
    (r.sector || '').includes(search.toLowerCase()) ||
    (r.keyword || '').includes(search.toLowerCase())
  )

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
          RULE MANAGEMENT
        </div>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 700,
          fontFamily: 'Inter, sans-serif',
          color: 'var(--text-primary)',
          letterSpacing: '-0.02em',
          marginBottom: '8px',
        }}>
          Classification Rules
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