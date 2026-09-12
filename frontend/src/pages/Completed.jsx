import FollowUpCard from '../components/FollowUpCard'
import WaitingCard from '../components/WaitingCard'
import EmptyState from '../components/EmptyState'
import { useProjectData, getStoredProjectId } from '../hooks/useProjectData'

export default function Completed() {
  const projectId = getStoredProjectId()
  const { commitments, waiting, loading, error, refresh } = useProjectData(projectId)

  if (!projectId) {
    return (
      <div>
        <h1 className="text-2xl font-semibold text-text">Completed</h1>
        <div className="mt-6">
          <EmptyState title="No completed follow-ups yet." />
        </div>
      </div>
    )
  }

  if (loading) return <p className="text-sm text-textMuted">Loading...</p>
  if (error) return <p className="text-sm text-red-400">{error}</p>

  const completedCommitments = commitments.filter((c) => c.status === 'completed')
  const resolvedWaiting = waiting.filter((w) => w.status === 'resolved')
  const isEmpty = completedCommitments.length === 0 && resolvedWaiting.length === 0

  return (
    <div>
      <h1 className="text-2xl font-semibold text-text">Completed</h1>
      <p className="mt-2 text-textSecondary">Everything you and your team have already closed out.</p>

      <div className="mt-6 space-y-3">
        {isEmpty ? (
          <EmptyState title="No completed follow-ups yet." />
        ) : (
          <>
            {completedCommitments.map((c) => (
              <FollowUpCard key={c.id} commitment={c} onChanged={refresh} />
            ))}
            {resolvedWaiting.map((w) => (
              <WaitingCard key={w.id} item={w} onChanged={refresh} />
            ))}
          </>
        )}
      </div>
    </div>
  )
}
