import { useAuth } from '../context/AuthContext.jsx'

export default function Nav() {
  const { user, logout } = useAuth()

  return (
    <header className="nav">
      <div className="nav__brand">
        <span className="nav__mark" aria-hidden="true" />
        <span className="nav__name">instascrapper</span>
        <span className="nav__tag">field station</span>
      </div>
      {user && (
        <div className="nav__right">
          <span className="nav__user">{user.username}</span>
          <button type="button" className="btn btn--ghost btn--sm" onClick={logout}>
            Sign out
          </button>
        </div>
      )}
    </header>
  )
}
