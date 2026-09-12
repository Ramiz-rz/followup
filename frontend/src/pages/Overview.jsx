import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useState } from 'react'
import StatCard from '../components/StatCard'
import RiskIndicator from '../components/RiskIndicator'
import EmptyState from '../components/EmptyState'
import { useProjectData, getStoredProjectId, setStoredProjectId } from '../hooks/useProjectData'
import * as api from '../lib/api'

export default function Overview() {
  const navigate = useNavigate()
  const projectId = getStoredProjectId()
  const { project, stats, forgotten, loading, error } = useProjectData(projectId)
  const [demoLoading, setDemoLoading] = useState(false)

  async function tryDemo() {
    setDemoLoading(true)
    try {
      const created = await api.runDemo()
      setStoredProjectId(created.id)
      navigate('/follow-ups')
      window.location.reload()
    } catch {
      setDemoLoading(false)
    }
  }

  if (!projectId || (!loading && !project)) {
    return (
      <div>
        <Header />
        <div className="mt-8 rounded-lg border border-border bg-surface px-6 py-14 text-center">
          <p className="text-text">Nothing analyzed yet.</p>
          <p className="mt-1 text-sm text-textMuted">
            Paste a conversation on the Analyze page, or try it with a sample first.
          </p>
          <div className="mt-5 flex justify-center gap-3">
            <button
              onClick={() => navigate('/analyze')}
              className="rounded bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90"
            >
              Analyze conversation
            </button>
            <button
              onClick={tryDemo}
              disabled={demoLoading}
              className="rounded border border-border px-4 py-2 text-sm text-textSecondary hover:text-text disabled:opacity-50"
            >
              {demoLoading ? 'Loading demo...' : 'Try demo'}
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div>
        <Header />
        <p className="mt-8 text-sm text-textMuted">Loading...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <Header />
        <p className="mt-8 text-sm text-red-400">{error}</p>
      </div>
    )
  }

  return (
    <div>
      <Header />

      <div className="mt-6 flex items-center justify-between">
        <div>
          <p className="text-sm text-textMuted">Current project</p>
          <p className="text-lg text-text">{project.name}</p>
        </div>
        <button
          onClick={() => navigate('/analyze')}
          className="rounded border border-border px-3 py-1.5 text-sm text-textSecondary hover:text-text"
        >
          Analyze more
        </button>
      </div>

      {project.summary && <p className="mt-3 text-sm text-textSecondary">{project.summary}</p>}

      <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
        <StatCard label="Open" value={stats.open} />
        <StatCard label="Due soon" value={stats.due_soon} accent="text-cyan" />
        <StatCard label="Overdue" value={stats.overdue} accent="text-red-400" />
        <StatCard label="Waiting" value={stats.waiting} accent="text-violet" />
      </div>

      <div className="mt-6">
        <RiskIndicator score={stats.risk_score} level={stats.risk_level} reasons={stats.risk_reasons} />
      </div>

      <div className="mt-8">
        <h2 className="text-sm font-medium text-text">Forgotten commitments</h2>
        <p className="mt-1 text-sm text-textMuted">These are commitments that look unresolved or overdue.</p>
        <div className="mt-4 space-y-3">
          {forgotten.length === 0 ? (
            <EmptyState title="Nothing looks forgotten right now." />
          ) : (
            forgotten.map((item, i) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: i * 0.03 }}
                className="rounded-lg border border-border bg-surface p-4"
              >
                <p className="text-[15px] text-text">{item.action}</p>
                <p className="mt-1 text-sm text-textSecondary">{item.person}</p>
                <p className="mt-2 rounded border border-border bg-surface2 px-3 py-2 font-mono text-sm text-textSecondary">
                  "{item.evidence}"
                </p>
                <p className="mt-2 text-sm text-amber-400">{item.reason}</p>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

function Header() {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-text">
        Good follow-ups start with things you already said.
      </h1>
      <p className="mt-2 text-textSecondary">
        Find commitments hidden in conversations before they get forgotten.
      </p>
    </div>
  )
}
