// API client for the Instascrapper backend.
//
// In development, requests go to "/api/..." and Vite proxies them to the
// Flask server (see vite.config.js). To point at a different backend, set
// VITE_API_BASE in a .env file (e.g. VITE_API_BASE=http://127.0.0.1:5000/api).

const BASE = import.meta.env.VITE_API_BASE || '/api'

const TOKEN_KEY = 'instascrapper_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

// Core request helper. Attaches the JWT, parses JSON, and throws an Error
// with the backend's message on non-2xx responses.
async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  let res
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch (networkErr) {
    throw new Error('Cannot reach the server. Is the backend running?')
  }

  let data = null
  const text = await res.text()
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = { error: text }
    }
  }

  if (!res.ok) {
    const message = (data && data.error) || `Request failed (${res.status})`
    const err = new Error(message)
    err.status = res.status
    throw err
  }

  return data
}

// ─── Auth ────────────────────────────────────────────────────────────────────

export const auth = {
  register: ({ username, email, password }) =>
    request('/auth/register', { method: 'POST', auth: false, body: { username, email, password } }),

  login: ({ username, password }) =>
    request('/auth/login', { method: 'POST', auth: false, body: { username, password } }),

  me: () => request('/auth/me'),
}

// ─── Jobs ────────────────────────────────────────────────────────────────────

export const jobs = {
  create: ({ hashtags, post_limit, sort_by }) =>
    request('/jobs', { method: 'POST', body: { hashtags, post_limit, sort_by } }),

  list: () => request('/jobs'),

  get: (uuid) => request(`/jobs/${uuid}`),

  remove: (uuid) => request(`/jobs/${uuid}`, { method: 'DELETE' }),

  // Download endpoint requires the Authorization header, so we can't use a
  // plain <a href>. Fetch the CSV as a blob, then trigger a browser download.
  async download(uuid, filename) {
    const token = getToken()
    const res = await fetch(`${BASE}/jobs/${uuid}/download`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (!res.ok) {
      let message = `Download failed (${res.status})`
      try {
        const data = await res.json()
        if (data.error) message = data.error
      } catch {
        /* keep default message */
      }
      throw new Error(message)
    }
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || `${uuid}.csv`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  },
}
