import { useState, useEffect } from 'react'
import { listRules } from '../api/client'

export default function Dashboard() {
  const [ruleCount, setRuleCount] = useState(null)

  useEffect(() => {
    listRules().then(res => setRuleCount(res.data.length))
  }, [])

  const stats = [
    { label: 'Active Rules', value: ruleCount ?? '...', desc: 'EU AI Act classification rules in database' },
    { label: 'Risk Tiers', value: '4', desc: 'Unacceptable, High, Limited, Minimal' },
    { label: 'OWASP Checks', value: '10', desc: 'LLM Top 10 risk categories assessed' },
    { label: 'NIST Functions', value: '4', desc: 'Govern, Map, Measure, Manage' },
  ]

  const capabilities = [
    { icon: '⬡', title: 'EU AI Act Classification', desc: 'Classify AI systems into risk tiers based on Annex III and Article 5 criteria. Generates sector-specific obligations.', link: '/classify' },
    { icon: '◎', title: 'RAG Compliance Assistant', desc: 'Ask natural language questions about the EU AI Act. Answers grounded in regulatory text with source citations.', link: '/assistant' },
    { icon: '◆', title: 'Rule Management', desc: 'Add, update, or deactivate classification rules without code changes. Full audit trail with timestamps.', link: '/admin' },
    { icon: '◷', title: 'Assessment History', desc: 'View past compliance assessments with full results and risk tier outcomes.', link: '/history' },
  ]

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '11px', color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: '8px' }}>
          EU AI ACT GOVERNANCE PLATFORM
        </div>
        <h1 style={{ fontSize: '28px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
          Compliance Dashboard
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)', maxWidth: '600px' }}>
          Automated AI governance platform for EU AI Act risk classification, DPIA generation, OWASP LLM assessment, and NIST AI RMF mapping.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '40px' }}>
        {stats.map(stat => (
          <div key={stat.label} style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border)',
            borderRadius: '6px',
            padding: '20px',
          }}>
            <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '28px', fontWeight: 600, color: 'var(--accent)', marginBottom: '4px' }}>
              {stat.value}
            </div>
            <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', marginBottom: '4px' }}>
              {stat.label}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              {stat.desc}
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
          Platform Capabilities
        </h2>
        <div style={{ width: '32px', height: '2px', background: 'var(--accent)', marginBottom: '20px' }} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
        {capabilities.map(cap => (
          <a key={cap.title} href={cap.link} style={{ textDecoration: 'none' }}>
            <div style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              padding: '24px',
              cursor: 'pointer',
              transition: 'border-color 0.15s ease',
            }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border-bright)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
            >
              <div style={{ fontSize: '20px', marginBottom: '12px' }}>{cap.icon}</div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
                {cap.title}
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {cap.desc}
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}