import { useState } from 'react'
import { useNavigate, Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Login() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to="/" replace />

  function update(key) {
    return (e) => setForm((f) => ({ ...f, [key]: e.target.value }))
  }

  async function handleSubmit() {
    if (!form.username || !form.password) {
      setError('Enter your username and password.')
      return
    }
    setSubmitting(true)
    setError('')
    try {
      await login(form)
      navigate('/', { replace: true })
    } catch (e) {
      setError(e.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth">
      <div className="auth__card">
        <h1 className="auth__title">Sign in</h1>
        <p className="auth__sub">Welcome back. Pick up where you left off.</p>

        <label className="field">
          <span className="field__label">Username</span>
          <input
            className="input"
            value={form.username}
            onChange={update('username')}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            autoComplete="username"
          />
        </label>

        <label className="field">
          <span className="field__label">Password</span>
          <input
            type="password"
            className="input"
            value={form.password}
            onChange={update('password')}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            autoComplete="current-password"
          />
        </label>

        {error && <p className="form-error" role="alert">{error}</p>}

        <button
          type="button"
          className="btn btn--primary btn--block"
          onClick={handleSubmit}
          disabled={submitting}
        >
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>

        <p className="auth__switch">
          No account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  )
}
