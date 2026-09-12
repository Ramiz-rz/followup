import { useState } from 'react'
import { motion } from 'framer-motion'
import { ChevronDown, CheckCircle2, Trash2 } from 'lucide-react'
import { ConfidenceBadge, StatusBadge } from './Badges'
import * as api from '../lib/api'

function daysSince(item) {
  const ref = item.waiting_since || item.created_at?.slice(0, 10)
  if (!ref) return null
  const start = new Date(ref)
  const now = new Date()
  const diff = Math.max(0, Math.floor((now - start) / (1000 * 60 * 60 * 24)))
  return diff
}

export default function WaitingCard({ item, onChanged }) {
  const [expanded, setExpanded] = useState(false)
  const [busy, setBusy] = useState(false)
  const days = daysSince(item)

  async function resolve() {
    setBusy(true)
    try {
      await api.updateWaiting(item.id, { status: 'resolved' })
      onChanged()
    } finally {
      setBusy(false)
    }
  }

  async function remove() {
    setBusy(true)
    try {
      await api.deleteWaiting(item.id)
      onChanged()
    } finally {
      setBusy(false)
    }
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="rounded-lg border border-border bg-surface p-4"
    >
      <p className="font-mono text-[11px] uppercase tracking-wide text-textMuted">Waiting on</p>
      <p className="mt-1 text-[15px] leading-snug text-text">{item.item}</p>
      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-textSecondary">
        <span>{item.person}</span>
        <span className="text-textMuted">&middot;</span>
        <span>{days !== null ? `Waiting ${days} day${days === 1 ? '' : 's'}` : 'Waiting since unclear'}</span>
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-3">
        <StatusBadge status={item.status} />
        <ConfidenceBadge confidence={item.confidence} />
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
          "{item.evidence}"
          {item.source && <span className="mt-1 block text-xs text-textMuted">Source: {item.source}</span>}
        </p>
      )}

      <div className="mt-4 flex gap-2">
        {item.status !== 'resolved' && (
          <button
            type="button"
            disabled={busy}
            onClick={resolve}
            className="flex items-center gap-1 rounded border border-border px-3 py-1.5 text-xs text-textSecondary hover:border-emerald-400/50 hover:text-emerald-400 disabled:opacity-50"
          >
            <CheckCircle2 size={13} /> Mark resolved
          </button>
        )}
        <button
          type="button"
          disabled={busy}
          onClick={remove}
          className="flex items-center gap-1 rounded border border-border px-3 py-1.5 text-xs text-textSecondary hover:border-red-400/50 hover:text-red-400 disabled:opacity-50"
        >
          <Trash2 size={13} /> Delete
        </button>
      </div>
    </motion.div>
  )
}
