import axios from 'axios'

const api = axios.create({
  baseURL: '/',
  headers: { 'Content-Type': 'application/json' }
})

export const classifySystem = (data) =>
  api.post('/api/v1/classify', data)

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

export default api


export const downloadReport = async (data) => {
  const response = await fetch('/api/v1/assess-and-download', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
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