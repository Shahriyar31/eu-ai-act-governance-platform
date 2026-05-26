export default function RiskBadge({ tier }) {
  const config = {
    unacceptable: { label: 'PROHIBITED', color: '#ff5d5d', bg: 'rgba(255, 93, 93, 0.12)' },
    high:         { label: 'HIGH RISK',  color: '#ffb020', bg: 'rgba(255, 176, 32, 0.12)' },
    limited:      { label: 'LIMITED',    color: '#4cc3ff', bg: 'rgba(76, 195, 255, 0.12)' },
    minimal:      { label: 'MINIMAL',    color: '#27d17f', bg: 'rgba(39, 209, 127, 0.12)' },
  }

  const c = config[tier] || config.minimal

  return (
    <span
      style={{
        backgroundColor: c.bg,
        color: c.color,
        border: `1px solid ${c.color}`,
        padding: '6px 12px',
        borderRadius: '999px',
        fontFamily: 'IBM Plex Mono, monospace',
        fontSize: '10px',
        fontWeight: 700,
        letterSpacing: '0.12em',
        textTransform: 'uppercase',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        lineHeight: 1,
      }}
    >
      {c.label}
    </span>
  )
}