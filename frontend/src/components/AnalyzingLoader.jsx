import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const STAGES = [
  'Reading conversation',
  'Finding commitments',
  'Checking dates',
  'Looking for waiting items',
  'Preparing follow-ups',
  'Calculating risk',
]

export default function AnalyzingLoader() {
  const [stage, setStage] = useState(0)

  useEffect(() => {
    const id = setInterval(() => {
      setStage((s) => (s + 1 < STAGES.length ? s + 1 : s))
    }, 900)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-border bg-surface px-6 py-14 text-center">
      <div className="mb-5 h-6 w-6 animate-spin rounded-full border-2 border-border border-t-accent" />
      <AnimatePresence mode="wait">
        <motion.p
          key={stage}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.2 }}
          className="text-sm text-textSecondary"
        >
          {STAGES[stage]}...
        </motion.p>
      </AnimatePresence>
    </div>
  )
}
