import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'

export default function EditModal({ title, fields, initialValues, onCancel, onSave }) {
  const [values, setValues] = useState(initialValues)
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    try {
      await onSave(values)
    } finally {
      setSaving(false)
    }
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-30 flex items-center justify-center bg-black/60 px-4"
        onClick={onCancel}
      >
        <motion.div
          initial={{ opacity: 0, y: 10, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 10, scale: 0.98 }}
          transition={{ duration: 0.15 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-md rounded-lg border border-borderStrong bg-surface p-5"
        >
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-medium text-text">{title}</h2>
            <button
              type="button"
              onClick={onCancel}
              aria-label="Close"
              className="rounded p-1 text-textMuted hover:text-text"
            >
              <X size={16} />
            </button>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            {fields.map((field) => (
              <div key={field.name}>
                <label className="mb-1 block text-xs text-textMuted" htmlFor={field.name}>
                  {field.label}
                </label>
                {field.type === 'select' ? (
                  <select
                    id={field.name}
                    value={values[field.name] ?? ''}
                    onChange={(e) => setValues({ ...values, [field.name]: e.target.value })}
                    className="w-full rounded border border-border bg-surface2 px-3 py-2 text-sm text-text"
                  >
                    {field.options.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                ) : field.type === 'textarea' ? (
                  <textarea
                    id={field.name}
                    value={values[field.name] ?? ''}
                    onChange={(e) => setValues({ ...values, [field.name]: e.target.value })}
                    rows={3}
                    className="w-full rounded border border-border bg-surface2 px-3 py-2 text-sm text-text"
                  />
                ) : (
                  <input
                    id={field.name}
                    type="text"
                    value={values[field.name] ?? ''}
                    onChange={(e) => setValues({ ...values, [field.name]: e.target.value })}
                    className="w-full rounded border border-border bg-surface2 px-3 py-2 text-sm text-text"
                  />
                )}
              </div>
            ))}
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={onCancel}
                className="rounded border border-border px-3 py-1.5 text-sm text-textSecondary hover:text-text"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="rounded bg-accent px-3 py-1.5 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save changes'}
              </button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
