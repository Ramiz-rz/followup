export default function EmptyState({ title, description }) {
  return (
    <div className="rounded border border-dashed border-border px-6 py-10 text-center">
      <p className="text-sm text-text">{title}</p>
      {description && <p className="mt-1 text-sm text-textMuted">{description}</p>}
    </div>
  )
}
