import Sidebar from './Sidebar'

export default function Layout({ children }) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{
        flex: 1,
        padding: '32px',
        overflowY: 'auto',
        background: 'var(--bg-base)',
      }}>
        {children}
      </main>
    </div>
  )
}