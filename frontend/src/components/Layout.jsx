import Sidebar from './Sidebar'

export default function Layout({ children }) {
  return (
    <div style={{
      display: 'flex',
      minHeight: '100vh',
      background:
        'radial-gradient(circle at top left, rgba(76,195,255,0.12), transparent 28%), radial-gradient(circle at top right, rgba(39,209,127,0.08), transparent 24%), var(--bg-base)',
    }}>
      <Sidebar />
      <main style={{
        flex: 1,
        padding: '28px',
        overflowY: 'auto',
        background: 'transparent',
      }}>
        {children}
      </main>
    </div>
  )
}