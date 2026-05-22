import { NavLink, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useTheme } from '../context/ThemeContext'
import { useAuth } from '../context/AuthContext'

const links = [
  { to: '/', label: 'Dashboard', icon: '▦' },
  { to: '/classify', label: 'Classify', icon: '⬡' },
  { to: '/assistant', label: 'AI Assistant', icon: '◎' },
  { to: '/history', label: 'History', icon: '◷' },
  { to: '/admin', label: 'Rules', icon: '◆' },
]

const themeOptions = [
  { id: 'dark', label: 'Regulatory Dark', desc: 'Default dark theme', color: '#64b5f6' },
  { id: 'light', label: 'Executive Light', desc: 'Clean professional', color: '#0969da' },
  { id: 'contrast', label: 'High Contrast', desc: 'Accessibility', color: '#ffcc00' },
]

export default function Sidebar() {
  const { theme, setTheme } = useTheme()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [showThemePanel, setShowThemePanel] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside style={{
      width: '240px',
      minHeight: '100vh',
      background: 'var(--bg-surface)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
    }}>
      <div style={{
        padding: '24px 20px',
        borderBottom: '1px solid var(--border)',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          marginBottom: '12px',
        }}>
          <div style={{
            width: '34px',
            height: '34px',
            background: 'var(--accent)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '15px',
            color: 'var(--bg-base)',
            fontWeight: 800,
            fontFamily: 'Inter, sans-serif',
            flexShrink: 0,
          }}>
            G
          </div>
          <div>
            <div style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: '15px',
              fontWeight: 700,
              color: 'var(--text-primary)',
              lineHeight: 1.2,
              letterSpacing: '-0.02em',
            }}>
              Governance Platform
            </div>
            <div style={{
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '10px',
              color: 'var(--text-secondary)',
              marginTop: '2px',
            }}>
              EU AI Act Compliance
            </div>
          </div>
        </div>

        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          background: 'var(--accent-dim)',
          border: '1px solid var(--accent)',
          borderRadius: '20px',
        }}>
          <div style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: 'var(--success)',
          }} />
          <span style={{
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '10px',
            color: 'var(--accent)',
            letterSpacing: '0.08em',
          }}>
            LIVE
          </span>
        </div>
      </div>

      <nav style={{ padding: '12px', flex: 1 }}>
        <div style={{
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '10px',
          color: 'var(--text-muted)',
          letterSpacing: '0.1em',
          padding: '4px 8px 8px',
        }}>
          NAVIGATION
        </div>
        {links.map(link => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/'}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '9px 12px',
              marginBottom: '2px',
              textDecoration: 'none',
              borderRadius: '8px',
              background: isActive ? 'var(--accent-dim)' : 'transparent',
              border: isActive ? '1px solid var(--accent)' : '1px solid transparent',
              transition: 'all 0.15s ease',
            })}
          >
            {({ isActive }) => (
              <>
                <span style={{
                  fontSize: '14px',
                  color: isActive ? 'var(--accent)' : 'var(--text-secondary)',
                  width: '18px',
                  textAlign: 'center',
                  flexShrink: 0,
                }}>
                  {link.icon}
                </span>
                <span style={{
                  fontFamily: 'IBM Plex Sans, sans-serif',
                  fontSize: '14px',
                  fontWeight: isActive ? 600 : 400,
                  color: isActive ? 'var(--accent)' : 'var(--text-primary)',
                }}>
                  {link.label}
                </span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div style={{
        padding: '12px',
        borderTop: '1px solid var(--border)',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 12px',
          marginBottom: '8px',
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
        }}>
          <div style={{ minWidth: 0 }}>
            <div style={{
              fontFamily: 'IBM Plex Sans, sans-serif',
              fontSize: '13px',
              fontWeight: 500,
              color: 'var(--text-primary)',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {user?.username}
            </div>
            <div style={{
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '10px',
              color: 'var(--text-secondary)',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {user?.email}
            </div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              background: 'transparent',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              padding: '4px 10px',
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '10px',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              flexShrink: 0,
              marginLeft: '8px',
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
            OUT
          </button>
        </div>

        <button
          onClick={() => setShowThemePanel(p => !p)}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '10px 12px',
            background: showThemePanel ? 'var(--accent-dim)' : 'var(--bg-elevated)',
            border: `1px solid ${showThemePanel ? 'var(--accent)' : 'var(--border)'}`,
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <span style={{ fontSize: '15px' }}>🎨</span>
          <div style={{ textAlign: 'left', flex: 1 }}>
            <div style={{
              fontFamily: 'IBM Plex Sans, sans-serif',
              fontSize: '13px',
              fontWeight: 500,
              color: 'var(--text-primary)',
            }}>
              Appearance
            </div>
            <div style={{
              fontFamily: 'IBM Plex Mono, monospace',
              fontSize: '10px',
              color: 'var(--text-secondary)',
              marginTop: '1px',
            }}>
              {themeOptions.find(t => t.id === theme)?.label}
            </div>
          </div>
          <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
            {showThemePanel ? '▲' : '▼'}
          </span>
        </button>

        {showThemePanel && (
          <div style={{
            marginTop: '8px',
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            overflow: 'hidden',
          }}>
            {themeOptions.map((t, i) => (
              <button
                key={t.id}
                onClick={() => { setTheme(t.id); setShowThemePanel(false) }}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '10px 12px',
                  background: theme === t.id ? 'var(--accent-dim)' : 'transparent',
                  border: 'none',
                  borderBottom: i < themeOptions.length - 1 ? '1px solid var(--border)' : 'none',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'background 0.15s ease',
                }}
              >
                <div style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  background: t.color,
                  flexShrink: 0,
                }} />
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontFamily: 'IBM Plex Sans, sans-serif',
                    fontSize: '13px',
                    fontWeight: theme === t.id ? 600 : 400,
                    color: theme === t.id ? 'var(--accent)' : 'var(--text-primary)',
                  }}>
                    {t.label}
                  </div>
                  <div style={{
                    fontFamily: 'IBM Plex Mono, monospace',
                    fontSize: '10px',
                    color: 'var(--text-secondary)',
                    marginTop: '1px',
                  }}>
                    {t.desc}
                  </div>
                </div>
                {theme === t.id && (
                  <span style={{ color: 'var(--accent)', fontSize: '13px' }}>✓</span>
                )}
              </button>
            ))}
          </div>
        )}

        <div style={{
          marginTop: '10px',
          padding: '0 4px',
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: '10px',
          color: 'var(--text-muted)',
        }}>
          v0.1.0 — Sprint 5
        </div>
      </div>
    </aside>
  )
}
