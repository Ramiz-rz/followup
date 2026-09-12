import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, X } from 'lucide-react'
import AnalyzingLoader from '../components/AnalyzingLoader'
import { setStoredProjectId } from '../hooks/useProjectData'
import * as api from '../lib/api'

const ACCEPTED = '.pdf,.txt,.md,.markdown,.json'

export default function Analyze() {
  const navigate = useNavigate()
  const fileRef = useRef(null)
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [projectName, setProjectName] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState(null)

  function handleFileChange(e) {
    const f = e.target.files?.[0]
    if (f) {
      setFile(f)
      setText('')
    }
  }

  function removeFile() {
    setFile(null)
    if (fileRef.current) fileRef.current.value = ''
  }

  async function submit(e) {
    e.preventDefault()
    setError(null)
    if (!file && !text.trim()) {
      setError('Add some conversation text first.')
      return
    }
    setAnalyzing(true)
    try {
      const project = file
        ? await api.analyzeFile(file, projectName)
        : await api.analyzeText(text, projectName)
      setStoredProjectId(project.id)
      navigate('/follow-ups')
      window.location.reload()
    } catch (err) {
      setError(err.message || 'Something went wrong while analyzing this.')
      setAnalyzing(false)
    }
  }

  async function useDemo() {
    setAnalyzing(true)
    try {
      const project = await api.runDemo()
      setStoredProjectId(project.id)
      navigate('/follow-ups')
      window.location.reload()
    } catch (err) {
      setError(err.message || 'Could not load the demo conversation.')
      setAnalyzing(false)
    }
  }

  if (analyzing) {
    return (
      <div>
        <PageHeader />
        <div className="mt-6">
          <AnalyzingLoader />
        </div>
      </div>
    )
  }

  return (
    <div>
      <PageHeader />

      <form onSubmit={submit} className="mt-6 space-y-5">
        <div>
          <label htmlFor="project-name" className="mb-1 block text-sm text-textSecondary">
            Project name (optional)
          </label>
          <input
            id="project-name"
            type="text"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="e.g. Atlas Client Portal"
            className="w-full rounded border border-border bg-surface px-3 py-2 text-sm text-text placeholder:text-textMuted"
          />
        </div>

        <div>
          <label htmlFor="conversation-text" className="mb-1 block text-sm text-textSecondary">
            Paste conversation
          </label>
          <textarea
            id="conversation-text"
            value={text}
            onChange={(e) => {
              setText(e.target.value)
              if (e.target.value) removeFile()
            }}
            rows={10}
            placeholder={'Client: Can we have the dashboard ready by Friday?\nDeveloper: I\'ll send a preview tomorrow.'}
            className="w-full rounded border border-border bg-surface px-3 py-3 text-sm text-text placeholder:text-textMuted"
          />
        </div>

        <div className="flex items-center gap-3">
          <div className="h-px flex-1 bg-border" />
          <span className="text-xs text-textMuted">or</span>
          <div className="h-px flex-1 bg-border" />
        </div>

        <div>
          <label className="mb-1 block text-sm text-textSecondary">Upload file</label>
          {file ? (
            <div className="flex items-center justify-between rounded border border-border bg-surface px-3 py-2 text-sm text-text">
              <span className="truncate">{file.name}</span>
              <button type="button" onClick={removeFile} aria-label="Remove file" className="text-textMuted hover:text-text">
                <X size={16} />
              </button>
            </div>
          ) : (
            <label className="flex cursor-pointer items-center justify-center gap-2 rounded border border-dashed border-border px-4 py-6 text-sm text-textMuted hover:border-borderStrong hover:text-textSecondary">
              <Upload size={16} />
              PDF, TXT, Markdown, or JSON
              <input
                ref={fileRef}
                type="file"
                accept={ACCEPTED}
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          )}
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            className="rounded bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90"
          >
            Find follow-ups
          </button>
          <button
            type="button"
            onClick={useDemo}
            className="rounded border border-border px-4 py-2 text-sm text-textSecondary hover:text-text"
          >
            Use demo conversation
          </button>
        </div>
      </form>
    </div>
  )
}

function PageHeader() {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-text">Find follow-ups</h1>
      <p className="mt-2 text-textSecondary">
        Paste a conversation or upload notes. FollowUp will look for commitments, waiting items,
        dates, and people.
      </p>
    </div>
  )
}
