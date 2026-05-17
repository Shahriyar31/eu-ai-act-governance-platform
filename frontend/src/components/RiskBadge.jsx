export default function RiskBadge({ tier }) {
  const config = {
    unacceptable: { label: 'PROHIBITED', color: '#ef4444', bg: '#1a0a0a' },
    high:         { label: 'HIGH RISK',  color: '#f59e0b', bg: '#1a1200' },
    limited:      { label: 'LIMITED',    color: '#3b82f6', bg: '#0a0f1a' },
    minimal:      { label: 'MINIMAL',    color: '#10b981', bg: '#0a1a12' },
  }

  const c = config[tier] || config.minimal

  return (
    <span
      style={{
        backgroundColor: c.bg,
        color: c.color,
        border: `1px solid ${c.color}`,
        padding: '2px 10px',
        borderRadius: '3px',
        fontFamily: 'IBM Plex Mono, monospace',
        fontSize: '11px',
        fontWeight: 600,
        letterSpacing: '0.08em',
      }}
    >
      {c.label}
    </span>
  )
}