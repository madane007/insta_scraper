import { useState } from 'react'

const MAX_HASHTAGS = 10
const MAX_POSTS = 500

export default function ScraperForm({ onSubmit, submitting }) {
  const [input, setInput] = useState('')
  const [tags, setTags] = useState([])
  const [postLimit, setPostLimit] = useState(50)
  const [sortBy, setSortBy] = useState('newest')
  const [error, setError] = useState('')

  function normalize(raw) {
    return raw.replace(/^#+/, '').trim().toLowerCase()
  }

  function commitTags(raw) {
    // Accept comma- or space-separated entries.
    const pieces = raw.split(/[,\s]+/).map(normalize).filter(Boolean)
    if (pieces.length === 0) return
    setTags((prev) => {
      const next = [...prev]
      for (const p of pieces) {
        if (!next.includes(p) && next.length < MAX_HASHTAGS) next.push(p)
      }
      return next
    })
    setInput('')
    setError('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      commitTags(input)
    } else if (e.key === 'Backspace' && input === '' && tags.length > 0) {
      setTags((prev) => prev.slice(0, -1))
    }
  }

  function removeTag(tag) {
    setTags((prev) => prev.filter((t) => t !== tag))
  }

  function handleSubmit() {
    // Fold any text still sitting in the input into the tag list.
    const pending = input ? input.split(/[,\s]+/).map(normalize).filter(Boolean) : []
    const allTags = [...new Set([...tags, ...pending])].slice(0, MAX_HASHTAGS)

    if (allTags.length === 0) {
      setError('Add at least one hashtag.')
      return
    }
    const limit = Number(postLimit)
    if (!Number.isInteger(limit) || limit < 1 || limit > MAX_POSTS) {
      setError(`Post limit must be a whole number between 1 and ${MAX_POSTS}.`)
      return
    }

    setTags(allTags)
    setInput('')
    setError('')
    onSubmit({ hashtags: allTags, post_limit: limit, sort_by: sortBy })
  }

  const atTagLimit = tags.length >= MAX_HASHTAGS

  return (
    <section className="form-card" aria-labelledby="scrape-heading">
      <div className="form-card__head">
        <h2 id="scrape-heading" className="form-card__title">Start a scrape</h2>
        <p className="form-card__sub">
          Collect public posts for up to {MAX_HASHTAGS} hashtags. Results arrive as a CSV.
        </p>
      </div>

      <label className="field">
        <span className="field__label">Hashtags</span>
        <div className={`tagbox ${atTagLimit ? 'tagbox--full' : ''}`}>
          {tags.map((tag) => (
            <span className="chip" key={tag}>
              <span className="chip__hash">#</span>{tag}
              <button
                type="button"
                className="chip__x"
                aria-label={`Remove ${tag}`}
                onClick={() => removeTag(tag)}
              >
                ×
              </button>
            </span>
          ))}
          <input
            className="tagbox__input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onBlur={() => input && commitTags(input)}
            placeholder={
              atTagLimit ? 'Limit reached' : tags.length ? 'Add another…' : 'e.g. python, datascience'
            }
            disabled={atTagLimit}
          />
        </div>
        <span className="field__hint">
          {tags.length}/{MAX_HASHTAGS} · press Enter or comma to add
        </span>
      </label>

      <div className="field-row">
        <label className="field field--limit">
          <span className="field__label">Post limit</span>
          <input
            type="number"
            className="input"
            min={1}
            max={MAX_POSTS}
            value={postLimit}
            onChange={(e) => setPostLimit(e.target.value)}
          />
          <span className="field__hint">1–{MAX_POSTS} posts</span>
        </label>

        <label className="field field--sort">
          <span className="field__label">Sort by</span>
          <div className="segmented">
            <button
              type="button"
              className={`segmented__btn ${sortBy === 'newest' ? 'is-active' : ''}`}
              onClick={() => setSortBy('newest')}
            >
              Newest first
            </button>
            <button
              type="button"
              className={`segmented__btn ${sortBy === 'oldest' ? 'is-active' : ''}`}
              onClick={() => setSortBy('oldest')}
            >
              Oldest first
            </button>
          </div>
        </label>
      </div>

      {error && <p className="form-error" role="alert">{error}</p>}

      <button
        type="button"
        className="btn btn--primary btn--block"
        onClick={handleSubmit}
        disabled={submitting}
      >
        {submitting ? 'Starting…' : 'Run scrape'}
      </button>
    </section>
  )
}
