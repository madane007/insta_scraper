import { useState } from 'react'
import { useNavigate, Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Register() {
  const { user, register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to="/" replace />

  function update(key) {
    return (e) => setForm((f) => ({ ...f, [key]: e.target.value }))
  }

  // Mirror the backend's validation so users get instant feedback.
  function validate() {
    const username = form.username.trim()
    const email = form.email.trim().toLowerCase()
    const password = form.password
    if (!username || !email || !password) return 'Fill in every field.'
    if (username.length < 3 || username.length > 80) return 'Username must be 3–80 characters.'
    if (password.length < 6) return 'Password must be at least 6 characters.'
    if (!email.includes('@')) return 'Enter a valid email address.'
    return null
  }

  async function handleSubmit() {
    const problem = validate()
    if (problem) {
      setError(problem)
      return
    }
    setSubmitting(true)
    setError('')
    try {
      await register({
        username: form.username.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
      })
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
        <h1 className="auth__title">Create account</h1>
        <p className="auth__sub">Set up a login to start collecting data.</p>

        <label className="field">
          <span className="field__label">Username</span>
          <input
            className="input"
            value={form.username}
            onChange={update('username')}
            autoComplete="username"
          />
          <span className="field__hint">3–80 characters</span>
        </label>

        <label className="field">
          <span className="field__label">Email</span>
          <input
            type="email"
            className="input"
            value={form.email}
            onChange={update('email')}
            autoComplete="email"
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
            autoComplete="new-password"
          />
          <span className="field__hint">At least 6 characters</span>
        </label>

        {error && <p className="form-error" role="alert">{error}</p>}

        <button
          type="button"
          className="btn btn--primary btn--block"
          onClick={handleSubmit}
          disabled={submitting}
        >
          {submitting ? 'Creating…' : 'Create account'}
        </button>

        <p className="auth__switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
