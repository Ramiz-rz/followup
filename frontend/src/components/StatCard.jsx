import { motion } from 'framer-motion'

export default function StatCard({ label, value, accent }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="rounded-lg border border-border bg-surface px-5 py-4"
    >
      <p className="font-mono text-xs uppercase tracking-wide text-textMuted">{label}</p>
      <p className={`mt-2 text-3xl font-semibold ${accent || 'text-text'}`}>{value}</p>
    </motion.div>
  )
}
