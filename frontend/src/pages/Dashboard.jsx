import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis } from 'recharts'
import { listRules, getHistory } from '../api/client'
import RiskBadge from '../components/RiskBadge'

function AnimatedCounter({ target, duration = 1200 }) {
  const [count, setCount] = useState(0)
  const startTime = useRef(null)

  useEffect(() => {
    if (!target) return
    const animate = (timestamp) => {
      if (!startTime.current) startTime.current = timestamp
      const elapsed = timestamp - startTime.current
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.floor(eased * target))
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [target, duration])

  return <span>{count}</span>
}

const RISK_COLORS = {
  unacceptable: '#f85149',
  high: '#d29922',
  limited: '#58a6ff',
  minimal: '#3fb950',
}

const CARD_STYLE = {
  background: 'var(--bg-surface)',
  border: '1px solid var(--border)',
  borderRadius: '12px',
  padding: '24px',
  transition: 'transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease',
  cursor: 'default',
}

function HoverCard({ children, onClick, style = {} }) {
  return (
    <div
      className="premium-tile"
      onClick={onClick}
      style={{
        ...CARD_STYLE,
        ...style,
        cursor: onClick ? 'pointer' : 'default',
        padding: '24px',
        borderRadius: '12px',
      }}
    >
      {children}
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [ruleCount, setRuleCount] = useState(0)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([listRules(), getHistory()])
      .then(([rulesRes, historyRes]) => {
        setRuleCount(rulesRes.data.length)
        setHistory(historyRes.data)
      })
      .finally(() => setLoading(false))
  }, [])

  const riskDistribution = Object.entries(
    history.reduce((acc, item) => {
      acc[item.risk_tier] = (acc[item.risk_tier] || 0) + 1
      return acc
    }, {})
  ).map(([name, value]) => ({ name, value }))

  const sectorDistribution = Object.entries(
    history.reduce((acc, item) => {
      const sector = item.sector.replace(/_/g, ' ')
      acc[sector] = (acc[sector] || 0) + 1
      return acc
    }, {})
  )
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 6)

  const stats = [
    { label: 'Active Rules', value: ruleCount, desc: 'Classification rules in DB' },
    { label: 'Risk Tiers', value: 4, desc: 'EU AI Act categories' },
    { label: 'OWASP Checks', value: 10, desc: 'LLM Top 10 assessed' },
    { label: 'Assessments', value: history.length, desc: 'Total classifications run' },
  ]

  const capabilities = [
    { icon: '⬡', title: 'EU AI Act Classification', desc: 'Classify systems into risk tiers based on Annex III and Article 5 criteria.', link: '/classify', color: '#58a6ff' },
    { icon: '◎', title: 'RAG Compliance Assistant', desc: 'Ask questions about the EU AI Act. Answers grounded in regulatory text.', link: '/assistant', color: '#3fb950' },
    { icon: '◆', title: 'Rule Management', desc: 'Add or deactivate classification rules without code changes.', link: '/admin', color: '#d29922' },
    { icon: '◷', title: 'Assessment History', desc: 'View past compliance assessments with full results and risk outcomes.', link: '/history', color: '#bc8cff' },
  ]

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
          EU AI ACT GOVERNANCE PLATFORM
        </div>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 700,
          fontFamily: 'Inter, sans-serif',
          color: 'var(--text-primary)',
          letterSpacing: '-0.02em',
          marginBottom: '8px',
        }}>
          Compliance Dashboard
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)', maxWidth: '600px' }}>
          Automated AI governance platform for EU AI Act risk classification, DPIA generation, OWASP LLM assessment, and NIST AI RMF mapping.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        {stats.map((stat, i) => (
          <HoverCard key={stat.label} style={{ animationDelay: `${i * 0.05}s` }}>
            <div style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: '36px',
              fontWeight: 700,
              color: 'var(--accent)',
              letterSpacing: '-0.02em',
              lineHeight: 1,
              marginBottom: '8px',
            }}>
              {loading ? '—' : <AnimatedCounter target={stat.value} />}
            </div>
            <div style={{
              fontSize: '14px',
              fontWeight: 600,
              color: 'var(--text-primary)',
              marginBottom: '4px',
            }}>
              {stat.label}
            </div>
            <div style={{
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '11px',
              color: 'var(--text-secondary)',
            }}>
              {stat.desc}
            </div>
          </HoverCard>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
        <HoverCard>
          <div style={{
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            marginBottom: '4px',
          }}>
            Risk Tier Distribution
          </div>
          <div style={{
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '11px',
            color: 'var(--text-secondary)',
            marginBottom: '20px',
          }}>
            {history.length} total assessments
          </div>
          {history.length === 0 ? (
            <div style={{
              height: '160px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '12px',
            }}>
              No assessments yet — classify a system first
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
              <ResponsiveContainer width={160} height={160}>
                <PieChart>
                  <Pie
                    data={riskDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={70}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {riskDistribution.map((entry) => (
                      <Cell
                        key={entry.name}
                        fill={RISK_COLORS[entry.name] || '#8b949e'}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: 'var(--bg-elevated)',
                      border: '1px solid var(--border)',
                      borderRadius: '6px',
                      fontSize: '12px',
                      color: 'var(--text-primary)',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {riskDistribution.map(entry => (
                  <div key={entry.name} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{
                      width: '10px',
                      height: '10px',
                      borderRadius: '2px',
                      background: RISK_COLORS[entry.name] || '#8b949e',
                      flexShrink: 0,
                    }} />
                    <span style={{
                      fontFamily: 'IBM Plex Mono, monospace',
                      fontSize: '11px',
                      color: 'var(--text-secondary)',
                      textTransform: 'capitalize',
                    }}>
                      {entry.name}
                    </span>
                    <span style={{
                      fontFamily: 'IBM Plex Mono, monospace',
                      fontSize: '11px',
                      color: 'var(--text-primary)',
                      fontWeight: 600,
                      marginLeft: 'auto',
                    }}>
                      {entry.value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </HoverCard>

        <HoverCard>
          <div style={{
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            marginBottom: '4px',
          }}>
            Assessments by Sector
          </div>
          <div style={{
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '11px',
            color: 'var(--text-secondary)',
            marginBottom: '20px',
          }}>
            Top sectors assessed
          </div>
          {sectorDistribution.length === 0 ? (
            <div style={{
              height: '160px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '12px',
            }}>
              No assessments yet
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={sectorDistribution} layout="vertical" margin={{ left: 0, right: 16 }}>
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={100}
                  tick={{
                    fontSize: 11,
                    fontFamily: 'IBM Plex Mono, monospace',
                    fill: 'var(--text-secondary)',
                  }}
                />
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border)',
                    borderRadius: '6px',
                    fontSize: '12px',
                    color: 'var(--text-primary)',
                  }}
                />
                <Bar dataKey="value" fill="var(--accent)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </HoverCard>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
        <div>
          <div style={{
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            marginBottom: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            Recent Assessments
            <span style={{
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '10px',
              color: 'var(--text-secondary)',
              fontWeight: 400,
            }}>
              — last {Math.min(history.length, 5)} of {history.length}
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {history.length === 0 ? (
              <div style={{
                padding: '20px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                color: 'var(--text-muted)',
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '12px',
                textAlign: 'center',
              }}>
                No assessments yet
              </div>
            ) : (
              history.slice(0, 5).map((item, i) => (
                <div
                  key={item.id}
                  onClick={() => navigate('/history')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px 16px',
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'border-color 0.15s ease, background 0.15s ease',
                    animation: `slideUp 0.3s ease ${i * 0.05}s both`,
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = 'var(--border-bright)'
                    e.currentTarget.style.background = 'var(--bg-elevated)'
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = 'var(--border)'
                    e.currentTarget.style.background = 'var(--bg-surface)'
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontSize: '13px',
                      fontWeight: 500,
                      color: 'var(--text-primary)',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}>
                      {item.system_name}
                    </div>
                    <div style={{
                      fontFamily: 'IBM Plex Mono, monospace',
                      fontSize: '10px',
                      color: 'var(--text-secondary)',
                      marginTop: '2px',
                    }}>
                      {item.sector.replace(/_/g, ' ')} · {new Date(item.assessed_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })}
                    </div>
                  </div>
                  <RiskBadge tier={item.risk_tier} />
                </div>
              ))
            )}
          </div>
        </div>

        <div>
          <div style={{
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            marginBottom: '12px',
          }}>
            Platform Capabilities
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            {capabilities.map(cap => (
              <HoverCard
                key={cap.title}
                onClick={() => navigate(cap.link)}
                style={{ padding: '16px' }}
              >
                <div style={{
                  fontSize: '20px',
                  marginBottom: '8px',
                  color: cap.color,
                }}>
                  {cap.icon}
                </div>
                <div style={{
                  fontSize: '12px',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  marginBottom: '4px',
                  lineHeight: 1.3,
                }}>
                  {cap.title}
                </div>
                <div style={{
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '10px',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.5,
                }}>
                  {cap.desc}
                </div>
              </HoverCard>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}