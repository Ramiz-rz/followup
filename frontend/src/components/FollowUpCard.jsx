import { useState } from 'react'
import { motion } from 'framer-motion'
import { ChevronDown, Check, Pencil, Trash2 } from 'lucide-react'
import { StatusBadge, PriorityLabel, ConfidenceBadge } from './Badges'
import EditModal from './EditModal'
import * as api from '../lib/api'

function formatDue(commitment) {
  if (commitment.status === 'overdue' && commitment.due_date) return `Due date passed`
  if (commitment.due_date_text && commitment.due_date_text !== 'Unclear') {
    return `Due ${commitment.due_date_text}`
  }
  return 'No due date found'
}

export default function FollowUpCard({ commitment, onChanged }) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const [busy, setBusy] = useState(false)

  async function complete() {
    setBusy(true)
    try {
      await api.updateCommitment(commitment.id, { status: 'completed' })
      onChanged()
    } finally {
      setBusy(false)
    }
  }

  async function remove() {
    setBusy(true)
    try {
      await api.deleteCommitment(commitment.id)
      onChanged()
    } finally {
      setBusy(false)
    }
  }

  async function save(values) {
    await api.updateCommitment(commitment.id, values)
    setEditing(false)
    onChanged()
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="rounded-lg border border-border bg-surface p-4"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-mono text-[11px] uppercase tracking-wide text-textMuted">Follow-up</p>
          <p className="mt-1 text-[15px] leading-snug text-text">{commitment.action}</p>
          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-textSecondary">
            <span>{commitment.person}</span>
            <span className="text-textMuted">&middot;</span>
            <span>{formatDue(commitment)}</span>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-3">
            <StatusBadge status={commitment.status} />
            <PriorityLabel priority={commitment.priority} />
            <ConfidenceBadge confidence={commitment.confidence} />
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="mt-3 flex items-center gap-1 text-xs text-textMuted hover:text-textSecondary"
        aria-expanded={expanded}
      >
        <ChevronDown size={13} className={`transition-transform ${expanded ? 'rotate-180' : ''}`} />
        Evidence
      </button>
      {expanded && (
        <p className="mt-2 rounded border border-border bg-surface2 px-3 py-2 font-mono text-sm text-textSecondary">
          "{commitment.evidence}"
          {commitment.source && (
            <span className="mt-1 block text-xs text-textMuted">Source: {commitment.source}</span>
          )}
        </p>
      )}

      <div className="mt-4 flex gap-2">
        {commitment.status !== 'completed' && (
          <button
            type="button"
            disabled={busy}
            onClick={complete}
            className="flex items-center gap-1 rounded border border-border px-3 py-1.5 text-xs text-textSecondary hover:border-emerald-400/50 hover:text-emerald-400 disabled:opacity-50"
          >
            <Check size={13} /> Complete
          </button>
        )}
        <button
          type="button"
          onClick={() => setEditing(true)}
          className="flex items-center gap-1 rounded border border-border px-3 py-1.5 text-xs text-textSecondary hover:text-text"
        >
          <Pencil size={13} /> Edit
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={remove}
          className="flex items-center gap-1 rounded border border-border px-3 py-1.5 text-xs text-textSecondary hover:border-red-400/50 hover:text-red-400 disabled:opacity-50"
        >
          <Trash2 size={13} /> Delete
        </button>
      </div>

      {editing && (
        <EditModal
          title="Edit follow-up"
          initialValues={{
            action: commitment.action,
            person: commitment.person,
            due_date_text: commitment.due_date_text,
            priority: commitment.priority,
            status: commitment.status === 'due_soon' || commitment.status === 'overdue' ? 'open' : commitment.status,
          }}
          fields={[
            { name: 'action', label: 'Action', type: 'textarea' },
            { name: 'person', label: 'Person', type: 'text' },
            { name: 'due_date_text', label: 'Due date (e.g. "tomorrow", "Friday")', type: 'text' },
            {
              name: 'priority',
              label: 'Priority',
              type: 'select',
              options: [
                { value: 'high', label: 'High' },
                { value: 'medium', label: 'Medium' },
                { value: 'low', label: 'Low' },
              ],
            },
            {
              name: 'status',
              label: 'Status',
              type: 'select',
              options: [
                { value: 'open', label: 'Open' },
                { value: 'waiting', label: 'Waiting' },
                { value: 'completed', label: 'Completed' },
              ],
            },
          ]}
          onCancel={() => setEditing(false)}
          onSave={save}
        />
      )}
    </motion.div>
  )
}
