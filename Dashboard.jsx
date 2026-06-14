import { useState, useEffect, useRef, useCallback } from 'react'
import { jobs as jobsApi } from '../api/client.js'
import ScraperForm from '../components/ScraperForm.jsx'
import JobCard from '../components/JobCard.jsx'

const POLL_INTERVAL = 3000 // ms

export default function Dashboard() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [banner, setBanner] = useState(null) // { type, text }
  const pollRef = useRef(null)

  const refresh = useCallback(async () => {
    const data = await jobsApi.list()
    // Newest jobs first by creation time.
    const sorted = [...data.jobs].sort((a, b) =>
      (b.created_at || '').localeCompare(a.created_at || '')
    )
    setJobs(sorted)
    return sorted
  }, [])

  // Initial load.
  useEffect(() => {
    refresh()
      .catch((e) => setBanner({ type: 'error', text: e.message }))
      .finally(() => setLoading(false))
  }, [refresh])

  // Poll while any job is still active.
  useEffect(() => {
    const hasActive = jobs.some((j) => j.status === 'pending' || j.status === 'running')
    if (!hasActive) {
      if (pollRef.current) clearInterval(pollRef.current)
      pollRef.current = null
      return
    }
    if (pollRef.current) return // already polling
    pollRef.current = setInterval(() => {
      refresh().catch(() => {/* keep last good state on transient errors */})
    }, POLL_INTERVAL)
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
      pollRef.current = null
    }
  }, [jobs, refresh])

  async function handleCreate(payload) {
    setSubmitting(true)
    setBanner(null)
    try {
      await jobsApi.create(payload)
      setBanner({ type: 'success', text: 'Scrape started. Progress will update below.' })
      await refresh()
    } catch (e) {
      setBanner({ type: 'error', text: e.message })
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDownload(job) {
    const filename = job.csv_filename || `${job.job_uuid}.csv`
    await jobsApi.download(job.job_uuid, filename)
  }

  async function handleDelete(job) {
    await jobsApi.remove(job.job_uuid)
    await refresh()
  }

  return (
    <div className="dashboard">
      <ScraperForm onSubmit={handleCreate} submitting={submitting} />

      {banner && (
        <p className={`banner banner--${banner.type}`} role="status">
          {banner.text}
        </p>
      )}

      <section className="jobs" aria-labelledby="jobs-heading">
        <div className="jobs__head">
          <h2 id="jobs-heading" className="jobs__title">Jobs</h2>
          {jobs.length > 0 && <span className="jobs__count">{jobs.length}</span>}
        </div>

        {loading ? (
          <p className="jobs__empty">Loading jobs…</p>
        ) : jobs.length === 0 ? (
          <div className="empty">
            <p className="empty__lead">No jobs yet.</p>
            <p className="empty__hint">Run a scrape above to collect your first dataset.</p>
          </div>
        ) : (
          <div className="jobs__list">
            {jobs.map((job) => (
              <JobCard
                key={job.job_uuid}
                job={job}
                onDownload={handleDownload}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
