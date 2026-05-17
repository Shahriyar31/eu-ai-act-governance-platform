import { NavLink } from 'react-router-dom'

const links = [
  { to: '/',          label: 'Dashboard',  icon: '◈' },
  { to: '/classify',  label: 'Classify',   icon: '⬡' },
  { to: '/assistant', label: 'AI Assistant', icon: '◎' },
  { to: '/history',   label: 'History',    icon: '◷' },
  { to: '/admin',     label: 'Rules',      icon: '◆' },
]

export default function Sidebar() {
  return (
    <aside style={{
      width: '220px',
      minHeight: '100vh',
      background: 'var(--bg-surface)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '0',
      flexShrink: 0,
    }}>
      <div style={{
        padding: '24px 20px',
        borderBottom: '1px solid var(--border)',
      }}>
        <div style={{
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '11px',
          color: 'var(--text-secondary)',
          letterSpacing: '0.12em',
          marginBottom: '4px',
        }}>
          EU AI ACT
        </div>
        <div style={{
          fontFamily: 'IBM Plex Sans, sans-serif',
          fontSize: '15px',
          fontWeight: 600,
          color: 'var(--text-primary)',
          lineHeight: 1.2,
        }}>
          Governance<br />Platform
        </div>
      </div>

      <nav style={{ padding: '12px 0', flex: 1 }}>
        {links.map(link => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/'}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '10px 20px',
              textDecoration: 'none',
              fontFamily: 'IBM Plex Sans, sans-serif',
              fontSize: '13px',
              fontWeight: isActive ? 500 : 400,
              color: isActive ? 'var(--accent)' : 'var(--text-secondary)',
              background: isActive ? 'rgba(245,158,11,0.06)' : 'transparent',
              borderLeft: isActive ? '2px solid var(--accent)' : '2px solid transparent',
              transition: 'all 0.15s ease',
            })}
          >
            <span style={{ fontSize: '14px', opacity: 0.8 }}>{link.icon}</span>
            {link.label}
          </NavLink>
        ))}
      </nav>

      <div style={{
        padding: '16px 20px',
        borderTop: '1px solid var(--border)',
        fontFamily: 'IBM Plex Mono, monospace',
        fontSize: '10px',
        color: 'var(--text-muted)',
      }}>
        v0.1.0 — Sprint 4
      </div>
    </aside>
  )
}