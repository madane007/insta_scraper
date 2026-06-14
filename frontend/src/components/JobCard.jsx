import { useState } from 'react'

const STATUS_META = {
  pending: { label: 'Queued', cls: 'is-pending' },
  running: { label: 'Running', cls: 'is-running' },
  completed: { label: 'Completed', cls: 'is-completed' },
  failed: { label: 'Failed', cls: 'is-failed' },
  cancelled: { label: 'Cancelled', cls: 'is-cancelled' },
}

function formatWhen(iso) {
  if (!iso) return null
  const d = new Date(iso + (iso.endsWith('Z') ? '' : 'Z')) // backend stores UTC
  if (Number.isNaN(d.getTime())) return null
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function JobCard({ job, onDownload, onDelete }) {
  const [busy, setBusy] = useState(null) // 'download' | 'delete' | null
  const [err, setErr] = useState('')

  const meta = STATUS_META[job.status] || { label: job.status, cls: '' }
  const isRunning = job.status === 'running' || job.status === 'pending'
  const isCompleted = job.status === 'completed'
  const when = formatWhen(job.completed_at || job.started_at || job.created_at)

  async function handleDownload() {
    setBusy('download')
    setErr('')
    try {
      await onDownload(job)
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy(null)
    }
  }

  async function handleDelete() {
    setBusy('delete')
    setErr('')
    try {
      await onDelete(job)
    } catch (e) {
      setErr(e.message)
      setBusy(null)
    }
    // On success the parent removes/refreshes this card, so no reset needed.
  }

  return (
    <article className={`job ${meta.cls}`}>
      <div className="job__main">
        <div className="job__tags">
          {job.hashtags.map((h) => (
            <span className="job__tag" key={h}>#{h}</span>
          ))}
        </div>
        <div className="job__meta">
          <span className={`pill ${meta.cls}`}>
            <span className="pill__dot" aria-hidden="true" />
            {meta.label}
          </span>
          <span className="job__count">
            {job.posts_count}/{job.post_limit} posts
          </span>
          {when && <span className="job__when">{when}</span>}
        </div>
      </div>

      <div className="job__track" aria-hidden="true">
        <div
          className={`job__fill ${isRunning ? 'job__fill--live' : ''}`}
          style={{ width: `${Math.max(job.progress || 0, isRunning ? 8 : 0)}%` }}
        />
      </div>

      <div className="job__foot">
        <code className="job__uuid">{job.job_uuid}</code>
        <div className="job__actions">
          {isCompleted && (
            <button
              type="button"
              className="btn btn--sm btn--solid"
              onClick={handleDownload}
              disabled={busy === 'download'}
            >
              {busy === 'download' ? 'Preparing…' : 'Download CSV'}
            </button>
          )}
          {job.status !== 'cancelled' && (
            <button
              type="button"
              className="btn btn--sm btn--ghost btn--danger"
              onClick={handleDelete}
              disabled={busy === 'delete'}
            >
              {busy === 'delete' ? 'Removing…' : 'Delete'}
            </button>
          )}
        </div>
      </div>

      {job.status === 'failed' && job.error_message && (
        <p className="job__error">{job.error_message}</p>
      )}
      {err && <p className="job__error">{err}</p>}
    </article>
  )
}
