import { useState, useEffect } from 'react'
import { getHistory } from '../api/client'
import RiskBadge from '../components/RiskBadge'

export default function History() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    getHistory()
      .then(res => setRecords(res.data))
      .finally(() => setLoading(false))
  }, [])

  const tiers = ['all', 'unacceptable', 'high', 'limited', 'minimal']

  const filtered = filter === 'all'
    ? records
    : records.filter(r => r.risk_tier === filter)

  const stats = [
    { label: 'Total records', value: records.length },
    { label: 'Prohibited', value: records.filter(r => r.risk_tier === 'unacceptable').length },
    { label: 'High risk', value: records.filter(r => r.risk_tier === 'high').length },
    { label: 'Limited / minimal', value: records.filter(r => ['limited', 'minimal'].includes(r.risk_tier)).length },
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
          Assessment history
        </div>
        <h1 style={{ fontSize: 'clamp(30px, 4vw, 46px)', fontWeight: 700, fontFamily: 'Inter, sans-serif', color: 'var(--text-primary)', letterSpacing: '-0.04em', marginBottom: '8px' }}>
          Past Assessments
        </h1>
        <p style={{ fontSize: '15px', color: 'var(--text-secondary)', maxWidth: '70ch', lineHeight: 1.7 }}>
          Review prior classifications, compare sectors, and scan the current risk distribution across the platform.
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

      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '16px' }}>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {tiers.map(t => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              style={{
                padding: '8px 14px',
                background: filter === t ? 'rgba(76,195,255,0.12)' : 'rgba(255,255,255,0.02)',
                border: `1px solid ${filter === t ? 'var(--accent)' : 'var(--border)'}`,
                borderRadius: '999px',
                color: filter === t ? 'var(--accent)' : 'var(--text-secondary)',
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '10px',
                fontWeight: 700,
                letterSpacing: '0.14em',
                textTransform: 'uppercase',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {t}
            </button>
          ))}
        </div>
        <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
          {filtered.length} records
        </div>
      </div>

      <div style={{ ...panel, overflow: 'hidden' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 2.2fr) minmax(0, 1fr) minmax(0, 1fr) 140px',
          padding: '14px 20px',
          borderBottom: '1px solid var(--border)',
          background: 'rgba(255,255,255,0.02)',
        }}>
          {['System name', 'Sector', 'Risk tier', 'Date'].map(h => (
            <div key={h} style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.14em', textTransform: 'uppercase' }}>
              {h}
            </div>
          ))}
        </div>

        {loading ? (
          <div style={{ padding: '56px', textAlign: 'center', fontFamily: 'IBM Plex Mono, monospace', fontSize: '12px', color: 'var(--text-secondary)' }}>
            Loading assessments...
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '72px 28px', display: 'grid', placeItems: 'center', textAlign: 'center' }}>
            <div>
              <div style={{ fontSize: '34px', opacity: 0.35, marginBottom: '12px' }}>◷</div>
              <div style={{ fontSize: '15px', color: 'var(--text-primary)', fontWeight: 600, marginBottom: '6px' }}>
                {filter === 'all' ? 'No assessments yet' : `No ${filter} risk assessments`}
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                Run a classification to populate the history ledger.
              </div>
            </div>
          </div>
        ) : (
          filtered.map((r, i) => (
            <div
              key={r.id}
              style={{
                display: 'grid',
                gridTemplateColumns: 'minmax(0, 2.2fr) minmax(0, 1fr) minmax(0, 1fr) 140px',
                padding: '16px 20px',
                borderBottom: i < filtered.length - 1 ? '1px solid var(--border)' : 'none',
                alignItems: 'center',
                gap: '12px',
                transition: 'background 0.15s ease',
                animation: `slideUp 0.3s ease ${i * 0.03}s both`,
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
                  {r.system_name}
                </div>
                <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                  Record #{r.id}
                </div>
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                {r.sector.replace(/_/g, ' ')}
              </div>
              <div>
                <RiskBadge tier={r.risk_tier} />
              </div>
              <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--text-secondary)' }}>
                {new Date(r.assessed_at).toLocaleDateString('en-GB', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric',
                })}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}