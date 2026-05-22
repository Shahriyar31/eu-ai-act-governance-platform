import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate, Link } from 'react-router-dom'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleLogin = async () => {
    if (!form.email || !form.password) return
    setLoading(true)
    setError(null)
    try {
      await login(form.email, form.password)
      navigate('/')
    } catch (e) {
      setError(e.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const inputStyle = {
    width: '100%',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    padding: '11px 14px',
    color: 'var(--text-primary)',
    fontFamily: 'IBM Plex Sans, sans-serif',
    fontSize: '14px',
    outline: 'none',
    boxSizing: 'border-box',
    transition: 'border-color 0.15s ease',
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-base)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <div style={{
        width: '420px',
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: '16px',
        padding: '40px',
        animation: 'slideUp 0.4s ease forwards',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            background: 'var(--accent)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '22px',
            fontWeight: 800,
            fontFamily: 'Inter, sans-serif',
            color: 'var(--bg-base)',
            margin: '0 auto 16px',
          }}>
            G
          </div>
          <h1 style={{
            fontSize: '22px',
            fontWeight: 700,
            fontFamily: 'Inter, sans-serif',
            color: 'var(--text-primary)',
            letterSpacing: '-0.02em',
            marginBottom: '4px',
          }}>
            Welcome back
          </h1>
          <p style={{
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontSize: '13px',
            color: 'var(--text-secondary)',
          }}>
            Sign in to EU AI Act Governance Platform
          </p>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{
            display: 'block',
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '11px',
            color: 'var(--text-secondary)',
            letterSpacing: '0.08em',
            marginBottom: '6px',
          }}>
            EMAIL
          </label>
          <input
            type="email"
            value={form.email}
            onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
            onKeyDown={e => e.key === 'Enter' && handleLogin()}
            placeholder="you@example.com"
            style={inputStyle}
            onFocus={e => e.target.style.borderColor = 'var(--accent)'}
            onBlur={e => e.target.style.borderColor = 'var(--border)'}
          />
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{
            display: 'block',
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '11px',
            color: 'var(--text-secondary)',
            letterSpacing: '0.08em',
            marginBottom: '6px',
          }}>
            PASSWORD
          </label>
          <input
            type="password"
            value={form.password}
            onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
            onKeyDown={e => e.key === 'Enter' && handleLogin()}
            placeholder="••••••••"
            style={inputStyle}
            onFocus={e => e.target.style.borderColor = 'var(--accent)'}
            onBlur={e => e.target.style.borderColor = 'var(--border)'}
          />
        </div>

        {error && (
          <div style={{
            marginBottom: '16px',
            padding: '10px 14px',
            background: 'rgba(248,81,73,0.08)',
            border: '1px solid var(--danger)',
            borderRadius: '8px',
            fontSize: '13px',
            color: 'var(--danger)',
            fontFamily: 'IBM Plex Sans, sans-serif',
          }}>
            {error}
          </div>
        )}

        <button
          onClick={handleLogin}
          disabled={loading || !form.email || !form.password}
          style={{
            width: '100%',
            padding: '13px',
            background: loading ? 'var(--bg-elevated)' : 'var(--accent)',
            color: loading ? 'var(--text-muted)' : 'var(--bg-base)',
            border: 'none',
            borderRadius: '8px',
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '12px',
            fontWeight: 600,
            letterSpacing: '0.08em',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'all 0.15s ease',
            marginBottom: '16px',
          }}
        >
          {loading ? 'SIGNING IN...' : 'SIGN IN →'}
        </button>

        <div style={{
          textAlign: 'center',
          fontFamily: 'IBM Plex Sans, sans-serif',
          fontSize: '13px',
          color: 'var(--text-secondary)',
        }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: 'var(--accent)', textDecoration: 'none', fontWeight: 500 }}>
            Create one
          </Link>
        </div>
      </div>
    </div>
  )
}