import { useState } from 'react'
import FollowUpCard from '../components/FollowUpCard'
import WaitingCard from '../components/WaitingCard'
import EmptyState from '../components/EmptyState'
import { useProjectData, getStoredProjectId } from '../hooks/useProjectData'

const TABS = ['All', 'Due soon', 'Overdue', 'Waiting', 'Completed']

const EMPTY_COPY = {
  All: ['No follow-ups yet.', 'No commitments have been added to this project.'],
  'Due soon': ['Nothing due soon.', ''],
  Overdue: ['Nothing is overdue.', ''],
  Waiting: ['Nothing is currently waiting on someone else.', ''],
  Completed: ['No completed follow-ups yet.', ''],
}

export default function FollowUps() {
  const projectId = getStoredProjectId()
  const { commitments, waiting, loading, error, refresh } = useProjectData(projectId)
  const [tab, setTab] = useState('All')

  if (!projectId) {
    return (
      <div>
        <h1 className="text-2xl font-semibold text-text">Follow-ups</h1>
        <div className="mt-6">
          <EmptyState
            title="No follow-ups yet."
            description="Analyze a conversation first to see follow-ups here."
          />
        </div>
      </div>
    )
  }

  if (loading) return <p className="text-sm text-textMuted">Loading...</p>
  if (error) return <p className="text-sm text-red-400">{error}</p>

  const visibleCommitments = commitments.filter((c) => {
    if (tab === 'All') return c.status !== 'completed'
    if (tab === 'Due soon') return c.status === 'due_soon'
    if (tab === 'Overdue') return c.status === 'overdue'
    if (tab === 'Waiting') return c.status === 'waiting'
    if (tab === 'Completed') return c.status === 'completed'
    return true
  })

  const visibleWaiting =
    tab === 'All' || tab === 'Waiting'
      ? waiting.filter((w) => w.status === 'waiting')
      : tab === 'Completed'
      ? waiting.filter((w) => w.status === 'resolved')
      : []

  const isEmpty = visibleCommitments.length === 0 && visibleWaiting.length === 0

  return (
    <div>
      <h1 className="text-2xl font-semibold text-text">Follow-ups</h1>

      <div className="mt-5 flex gap-1 overflow-x-auto border-b border-border">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`whitespace-nowrap border-b-2 px-3 py-2 text-sm ${
              tab === t
                ? 'border-accent text-text'
                : 'border-transparent text-textMuted hover:text-textSecondary'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="mt-5 space-y-3">
        {isEmpty ? (
          <EmptyState title={EMPTY_COPY[tab][0]} description={EMPTY_COPY[tab][1]} />
        ) : (
          <>
            {visibleCommitments.map((c) => (
              <FollowUpCard key={c.id} commitment={c} onChanged={refresh} />
            ))}
            {visibleWaiting.map((w) => (
              <WaitingCard key={w.id} item={w} onChanged={refresh} />
            ))}
          </>
        )}
      </div>
    </div>
  )
}
