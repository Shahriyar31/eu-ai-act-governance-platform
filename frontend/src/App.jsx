import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Classify from './pages/Classify'
import Assistant from './pages/Assistant'
import History from './pages/History'
import Admin from './pages/Admin'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/"          element={<Dashboard />} />
          <Route path="/classify"  element={<Classify />} />
          <Route path="/assistant" element={<Assistant />} />
          <Route path="/history"   element={<History />} />
          <Route path="/admin"     element={<Admin />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}