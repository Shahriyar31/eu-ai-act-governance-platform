import { useState, useEffect } from 'react'
import { listRules, deactivateRule } from '../api/client'
import RiskBadge from '../components/RiskBadge'

export default function Admin() {
  const [rules, setRules] = useState([])
  const [loading, setLoading] = useState(true)
  const [includeInactive, setIncludeInactive] = useState(false)
  const [confirming, setConfirming] = useState(null)

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

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: '8px' }}>
          RULE MANAGEMENT
        </div>
        <h1 style={{ fontSize: '28px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
          Classification Rules
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          Manage EU AI Act classification rules. Changes take effect immediately — no deployment required.
        </p>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '13px', color: 'var(--text-secondary)' }}>
          {rules.length} rules
        </div>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={e => setIncludeInactive(e.target.checked)}
            style={{ accentColor: 'var(--accent)' }}
          />
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontFamily: 'IBM Plex Sans, sans-serif' }}>
            Show inactive rules
          </span>
        </label>
      </div>

      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: '6px',
        overflow: 'hidden',
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '0.5fr 1fr 1fr 2fr 0.8fr',
          padding: '12px 20px',
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-elevated)',
        }}>
          {['PRIORITY', 'CONDITION', 'RISK TIER', 'JUSTIFICATION', 'STATUS'].map(h => (
            <div key={h} style={{
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '11px',
              color: 'var(--text-secondary)',
              letterSpacing: '0.08em',
            }}>
              {h}
            </div>
          ))}
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'IBM Plex Mono, monospace', fontSize: '13px', color: 'var(--text-secondary)' }}>
            Loading rules...
          </div>
        ) : (
          rules.map(rule => (
            <div key={rule.id} style={{
              display: 'grid',
              gridTemplateColumns: '0.5fr 1fr 1fr 2fr 0.8fr',
              padding: '14px 20px',
              borderBottom: '1px solid var(--border)',
              opacity: rule.is_active ? 1 : 0.4,
              alignItems: 'center',
            }}>
              <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '13px', color: 'var(--accent)' }}>
                {rule.priority}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontFamily: 'IBM Plex Mono, monospace' }}>
                {rule.keyword ? `keyword: "${rule.keyword}"` : rule.sector ? `sector: ${rule.sector}` : rule.interacts_with_humans ? 'interacts_with_humans' : 'fallback'}
              </div>
              <div>
                <RiskBadge tier={rule.risk_tier} />
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5, paddingRight: '16px' }}>
                {rule.justification_template.length > 80
                  ? rule.justification_template.slice(0, 80) + '...'
                  : rule.justification_template}
              </div>
              <div>
                {rule.is_active ? (
                  confirming === rule.id ? (
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => handleDeactivate(rule.id)}
                        style={{ padding: '4px 10px', background: 'var(--danger)', border: 'none', borderRadius: '3px', color: '#fff', fontSize: '11px', fontFamily: 'IBM Plex Mono, monospace', cursor: 'pointer' }}
                      >
                        CONFIRM
                      </button>
                      <button
                        onClick={() => setConfirming(null)}
                        style={{ padding: '4px 10px', background: 'transparent', border: '1px solid var(--border)', borderRadius: '3px', color: 'var(--text-secondary)', fontSize: '11px', fontFamily: 'IBM Plex Mono, monospace', cursor: 'pointer' }}
                      >
                        CANCEL
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setConfirming(rule.id)}
                      style={{ padding: '4px 10px', background: 'transparent', border: '1px solid var(--border)', borderRadius: '3px', color: 'var(--text-secondary)', fontSize: '11px', fontFamily: 'IBM Plex Mono, monospace', cursor: 'pointer' }}
                    >
                      DEACTIVATE
                    </button>
                  )
                ) : (
                  <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--text-muted)' }}>
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