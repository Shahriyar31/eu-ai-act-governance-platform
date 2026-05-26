import axios from 'axios'

export const API_URL = import.meta.env.VITE_API_URL || '/'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
})

// tracks whether a refresh is already in progress
// prevents multiple simultaneous refresh calls when several requests fail at once
let isRefreshing = false

// queue of requests that failed while refresh was in progress
// they all get retried once the new token arrives
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  failedQueue = []
}

// attach access token to every outgoing request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  return config
})

// catch 401 responses and transparently refresh the token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // only intercept 401 errors that haven't already been retried
    if (error.response?.status === 401 && !originalRequest._retry) {

      // if refresh is already happening, queue this request
      // it will be retried once the refresh completes
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`
          return api(originalRequest)
        }).catch(err => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')

      if (!refreshToken) {
        // no refresh token means user must log in again
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        // call refresh endpoint with the stored refresh token
        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken
        })

        const { access_token, refresh_token: newRefreshToken } = response.data

        // store new tokens — old refresh token is now revoked on server
        localStorage.setItem('auth_token', access_token)
        localStorage.setItem('refresh_token', newRefreshToken)
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

        // retry all queued requests with the new token
        processQueue(null, access_token)

        // retry the original request that triggered the 401
        originalRequest.headers['Authorization'] = `Bearer ${access_token}`
        return api(originalRequest)

      } catch (refreshError) {
        // refresh failed — session is truly expired, force login
        processQueue(refreshError, null)
        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('auth_user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

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

export const downloadReport = async (data) => {
  const token = localStorage.getItem('auth_token')
  const response = await fetch(`${API_URL}/api/v1/assess-and-download`, {
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

export default api