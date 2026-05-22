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
          ASSESSMENT HISTORY
        </div>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 700,
          fontFamily: 'Inter, sans-serif',
          color: 'var(--text-primary)',
          letterSpacing: '-0.02em',
          marginBottom: '8px',
        }}>
          Past Assessments
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          View all previous AI system classifications and their compliance outcomes.
        </p>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
      }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          {tiers.map(t => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              style={{
                padding: '6px 14px',
                background: filter === t ? 'var(--accent-dim)' : 'var(--bg-surface)',
                border: `1px solid ${filter === t ? 'var(--accent)' : 'var(--border)'}`,
                borderRadius: '20px',
                color: filter === t ? 'var(--accent)' : 'var(--text-secondary)',
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '11px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                textTransform: 'capitalize',
              }}
            >
              {t}
            </button>
          ))}
        </div>
        <div style={{
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '11px',
          color: 'var(--text-secondary)',
        }}>
          {filtered.length} records
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
          gridTemplateColumns: '2fr 1fr 1fr 1fr',
          padding: '12px 20px',
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-elevated)',
        }}>
          {['SYSTEM NAME', 'SECTOR', 'RISK TIER', 'ASSESSED'].map(h => (
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
            Loading...
          </div>
        ) : filtered.length === 0 ? (
          <div style={{
            padding: '64px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '12px',
          }}>
            <div style={{ fontSize: '32px', opacity: 0.2 }}>◷</div>
            <div style={{
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '13px',
              color: 'var(--text-secondary)',
            }}>
              {filter === 'all' ? 'No assessments yet' : `No ${filter} risk assessments`}
            </div>
          </div>
        ) : (
          filtered.map((r, i) => (
            <div
              key={r.id}
              style={{
                display: 'grid',
                gridTemplateColumns: '2fr 1fr 1fr 1fr',
                padding: '14px 20px',
                borderBottom: i < filtered.length - 1 ? '1px solid var(--border)' : 'none',
                alignItems: 'center',
                transition: 'background 0.15s ease',
                animation: `slideUp 0.3s ease ${i * 0.03}s both`,
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-elevated)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <div>
                <div style={{
                  fontSize: '14px',
                  fontWeight: 500,
                  color: 'var(--text-primary)',
                }}>
                  {r.system_name}
                </div>
                <div style={{
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '11px',
                  color: 'var(--text-muted)',
                  marginTop: '2px',
                }}>
                  #{r.id}
                </div>
              </div>
              <div style={{
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '12px',
                color: 'var(--text-secondary)',
                textTransform: 'capitalize',
              }}>
                {r.sector.replace(/_/g, ' ')}
              </div>
              <div>
                <RiskBadge tier={r.risk_tier} />
              </div>
              <div style={{
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '11px',
                color: 'var(--text-secondary)',
              }}>
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