const STATUS_STYLES = {
  open: 'text-textSecondary border-border',
  due_soon: 'text-cyan border-cyan/40',
  overdue: 'text-red-400 border-red-400/40',
  completed: 'text-emerald-400 border-emerald-400/40',
  waiting: 'text-violet border-violet/40',
  resolved: 'text-emerald-400 border-emerald-400/40',
}

const STATUS_LABELS = {
  open: 'Open',
  due_soon: 'Due soon',
  overdue: 'Overdue',
  completed: 'Completed',
  waiting: 'Waiting',
  resolved: 'Resolved',
}

export function StatusBadge({ status }) {
  const style = STATUS_STYLES[status] || STATUS_STYLES.open
  const label = STATUS_LABELS[status] || status
  return (
    <span className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-mono ${style}`}>
      {label}
    </span>
  )
}

const PRIORITY_STYLES = {
  high: 'text-red-400',
  medium: 'text-textSecondary',
  low: 'text-textMuted',
}

export function PriorityLabel({ priority }) {
  if (!priority) return null
  const label = priority.charAt(0).toUpperCase() + priority.slice(1)
  return <span className={`text-xs font-mono ${PRIORITY_STYLES[priority] || ''}`}>{label} priority</span>
}

function confidenceLabel(confidence) {
  if (confidence >= 0.75) return 'High'
  if (confidence >= 0.5) return 'Medium'
  return 'Low'
}

export function ConfidenceBadge({ confidence }) {
  const label = confidenceLabel(confidence)
  return (
    <span className="text-xs font-mono text-textMuted" title="How clearly the source text supports this extraction">
      Confidence: {label}
    </span>
  )
}
