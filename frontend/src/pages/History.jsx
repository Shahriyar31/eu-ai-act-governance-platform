import { useState, useEffect } from 'react'
import { getHistory } from '../api/client'
import RiskBadge from '../components/RiskBadge'

export default function History() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getHistory()
      .then(res => setRecords(res.data))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: '8px' }}>
          ASSESSMENT HISTORY
        </div>
        <h1 style={{ fontSize: '28px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
          Past Assessments
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          View all previous AI system classifications and their compliance outcomes.
        </p>
      </div>

      <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '6px', overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', padding: '12px 20px', borderBottom: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
          {['SYSTEM NAME', 'SECTOR', 'RISK TIER', 'ASSESSED'].map(h => (
            <div key={h} style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--text-secondary)', letterSpacing: '0.08em' }}>
              {h}
            </div>
          ))}
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'IBM Plex Mono, monospace', fontSize: '13px', color: 'var(--text-secondary)' }}>
            Loading...
          </div>
        ) : records.length === 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 20px' }}>
            <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '32px', marginBottom: '16px', opacity: 0.3 }}>◷</div>
            <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>No assessments yet</div>
            <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Classifications will appear here after you assess AI systems</div>
          </div>
        ) : (
          records.map(r => (
            <div key={r.id} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', padding: '14px 20px', borderBottom: '1px solid var(--border)', alignItems: 'center' }}>
              <div style={{ fontSize: '13px', color: 'var(--text-primary)', fontWeight: 500 }}>{r.system_name}</div>
              <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '12px', color: 'var(--text-secondary)' }}>
                {r.sector.replace(/_/g, ' ')}
              </div>
              <div><RiskBadge tier={r.risk_tier} /></div>
              <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--text-secondary)' }}>
                {new Date(r.assessed_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}