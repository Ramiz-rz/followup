import { motion } from 'framer-motion'

const LEVEL_COLOR = {
  Low: 'text-emerald-400',
  Medium: 'text-cyan',
  High: 'text-amber-400',
  Critical: 'text-red-400',
}

export default function RiskIndicator({ score, level, reasons }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="rounded-lg border border-border bg-surface px-5 py-5"
    >
      <p className="font-mono text-xs uppercase tracking-wide text-textMuted">Follow-Up Risk</p>
      <div className="mt-2 flex items-baseline gap-3">
        <span className="text-4xl font-semibold text-text">{score}</span>
        <span className="text-sm text-textMuted">/ 100</span>
        <span className={`text-sm font-medium ${LEVEL_COLOR[level] || 'text-text'}`}>{level}</span>
      </div>
      {reasons && reasons.length > 0 && (
        <div className="mt-4 border-t border-border pt-3">
          <p className="mb-2 text-xs text-textMuted">Why?</p>
          <ul className="space-y-1">
            {reasons.map((reason, i) => (
              <li key={i} className="text-sm text-textSecondary">
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  )
}
