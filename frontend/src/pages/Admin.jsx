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

  const stats = [
    { label: 'Active rules', value: rules.filter(r => r.is_active).length },
    { label: 'Prohibited', value: rules.filter(r => r.risk_tier === 'unacceptable').length },
    { label: 'High risk', value: rules.filter(r => r.risk_tier === 'high').length },
    { label: 'Inactive', value: rules.filter(r => !r.is_active).length },
  ]

  const panel = {
    background: 'linear-gradient(180deg, rgba(255,255,255,0.02), transparent 22%), var(--bg-glass)',
    border: '1px solid var(--border-glass)',
    borderRadius: '20px',
    boxShadow: 'var(--shadow-card)',
    backdropFilter: 'var(--blur)',
    WebkitBackdropFilter: 'var(--blur)',
  }

  return (
    <div style={{ animation: 'slideUp 0.4s ease forwards', maxWidth: 1440 }}>
      <div style={{ marginBottom: '24px' }}>
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
          Rule management
        </div>
        <h1 style={{ fontSize: 'clamp(30px, 4vw, 46px)', fontWeight: 700, fontFamily: 'Inter, sans-serif', color: 'var(--text-primary)', letterSpacing: '-0.04em', marginBottom: '8px' }}>
          Classification Rules
        </h1>
        <p style={{ fontSize: '15px', color: 'var(--text-secondary)', maxWidth: '70ch', lineHeight: 1.7 }}>
          Manage the live rule engine behind the classification workflow. Updates take effect immediately.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px', marginBottom: '20px' }}>
        {stats.map(stat => (
          <div key={stat.label} style={{ ...panel, padding: '18px' }}>
            <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: '10px' }}>
              {stat.label}
            </div>
            <div style={{ fontSize: '26px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.04em' }}>
              {stat.value}
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <input
          placeholder="Search rules..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{
            flex: '1 1 320px',
            background: 'rgba(255,255,255,0.02)',
            border: '1px solid var(--border)',
            borderRadius: '14px',
            padding: '12px 14px',
            color: 'var(--text-primary)',
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontSize: '14px',
            outline: 'none',
          }}
        />
        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          cursor: 'pointer',
          padding: '12px 14px',
          background: 'rgba(255,255,255,0.02)',
          border: '1px solid var(--border)',
          borderRadius: '14px',
          whiteSpace: 'nowrap',
        }}>
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={e => setIncludeInactive(e.target.checked)}
            style={{ accentColor: 'var(--accent)' }}
          />
          <span style={{ fontFamily: 'IBM Plex Sans, sans-serif', fontSize: '13px', color: 'var(--text-secondary)' }}>
            Show inactive
          </span>
        </label>
        <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.12em', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>
          {filtered.length} rules
        </div>
      </div>

      <div style={{ ...panel, overflow: 'hidden' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '72px minmax(0, 1.1fr) 170px minmax(0, 1.8fr) 140px',
          padding: '14px 20px',
          borderBottom: '1px solid var(--border)',
          background: 'rgba(255,255,255,0.02)',
        }}>
          {['Priority', 'Condition', 'Tier', 'Justification', 'Action'].map(h => (
            <div key={h} style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.14em', textTransform: 'uppercase' }}>
              {h}
            </div>
          ))}
        </div>

        {loading ? (
          <div style={{ padding: '56px', textAlign: 'center', fontFamily: 'IBM Plex Mono, monospace', fontSize: '12px', color: 'var(--text-secondary)' }}>
            Loading rules...
          </div>
        ) : (
          filtered.map((rule, i) => (
            <div
              key={rule.id}
              style={{
                display: 'grid',
                gridTemplateColumns: '72px minmax(0, 1.1fr) 170px minmax(0, 1.8fr) 140px',
                padding: '16px 20px',
                borderBottom: i < filtered.length - 1 ? '1px solid var(--border)' : 'none',
                alignItems: 'center',
                gap: '12px',
                opacity: rule.is_active ? 1 : 0.55,
                transition: 'background 0.15s ease',
                animation: `slideUp 0.3s ease ${i * 0.02}s both`,
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '20px', fontWeight: 700, color: 'var(--accent)', opacity: 0.75 }}>
                {rule.priority}
              </div>

              <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
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

              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.6, paddingRight: '12px' }}>
                {rule.justification_template}
              </div>

              <div>
                {rule.is_active ? (
                  confirming === rule.id ? (
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <button
                        onClick={() => handleDeactivate(rule.id)}
                        style={{
                          padding: '8px 12px',
                          background: 'rgba(248,81,73,0.1)',
                          border: '1px solid var(--danger)',
                          borderRadius: '12px',
                          color: 'var(--danger)',
                          fontFamily: 'IBM Plex Mono, monospace',
                          fontSize: '10px',
                          fontWeight: 700,
                          letterSpacing: '0.12em',
                          textTransform: 'uppercase',
                          cursor: 'pointer',
                        }}
                      >
                        Confirm
                      </button>
                      <button
                        onClick={() => setConfirming(null)}
                        style={{
                          padding: '8px 12px',
                          background: 'transparent',
                          border: '1px solid var(--border)',
                          borderRadius: '12px',
                          color: 'var(--text-secondary)',
                          fontFamily: 'IBM Plex Mono, monospace',
                          fontSize: '10px',
                          fontWeight: 700,
                          letterSpacing: '0.12em',
                          textTransform: 'uppercase',
                          cursor: 'pointer',
                        }}
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setConfirming(rule.id)}
                      style={{
                        padding: '8px 12px',
                        background: 'rgba(255,255,255,0.02)',
                        border: '1px solid var(--border)',
                        borderRadius: '12px',
                        color: 'var(--text-secondary)',
                        fontFamily: 'IBM Plex Mono, monospace',
                        fontSize: '10px',
                        fontWeight: 700,
                        letterSpacing: '0.12em',
                        textTransform: 'uppercase',
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
                      Deactivate
                    </button>
                  )
                ) : (
                  <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
                    Inactive
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