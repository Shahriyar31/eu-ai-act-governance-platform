import axios from 'axios'

const api = axios.create({
  baseURL: '/',
  headers: { 'Content-Type': 'application/json' }
})

// 🔑 THE FIX: Interceptor — attach JWT token before EVERY request
// Think of it as a checkpoint guard that checks your badge before
// letting Messenger B (this api instance) leave the building!
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

export const classifySystem = (data, version = 'v1') =>
  api.post(version === 'v2' ? '/api/v2/classify' : '/api/v1/classify', data)

export const runFullAssessment = (data) =>
  api.post('/api/v1/assess', data)

export const askQuestion = (question) =>
  api.post('/api/v1/ai/ask', { question })

export const listRules = (includeInactive = false) =>
  api.get(`/admin/rules?include_inactive=${includeInactive}`)

export const createRule = (data) =>
  api.post('/admin/rules', data)

export const updateRule = (id, data) =>
  api.patch(`/admin/rules/${id}`, data)

export const deactivateRule = (id) =>
  api.delete(`/admin/rules/${id}`)

export const getHistory = () =>
  api.get('/api/v1/history')

export const verifyLedger = () =>
  api.get('/api/v1/verify-ledger')

export const injectTamper = () =>
  api.post('/api/v1/sandbox/tamper')

export const restoreLedger = () =>
  api.post('/api/v1/sandbox/restore')

export const generateTraffic = () =>
  api.post('/api/v1/sandbox/traffic')

export default api


// Also fix downloadReport — it uses raw fetch(), so we attach the token manually
export const downloadReport = async (data) => {
  const token = localStorage.getItem('auth_token')
  const response = await fetch('/api/v1/assess-and-download', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Report generation failed')
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${data.system_name}_compliance_report.pdf`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}