import { NavLink } from 'react-router-dom'
import { LayoutGrid, ListChecks, Search, CheckCircle2, Menu, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getHealth } from '../lib/api'

const NAV_ITEMS = [
  { to: '/', label: 'Overview', icon: LayoutGrid, end: true },
  { to: '/follow-ups', label: 'Follow-ups', icon: ListChecks },
  { to: '/analyze', label: 'Analyze', icon: Search },
  { to: '/completed', label: 'Completed', icon: CheckCircle2 },
]

function ModeIndicator({ mode }) {
  if (!mode) return null
  const isAi = mode === 'ai'
  return (
    <div className="flex items-center gap-2 rounded border border-border px-3 py-2 text-xs font-mono">
      <span
        className={`h-1.5 w-1.5 rounded-full ${isAi ? 'bg-cyan' : 'bg-violet'}`}
        aria-hidden="true"
      />
      <span className="text-textSecondary">{isAi ? 'AI Mode' : 'Local Mode'}</span>
    </div>
  )
}

function NavLinks({ onNavigate }) {
  return (
    <nav className="flex flex-col gap-1" aria-label="Main navigation">
      {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded px-3 py-2 text-sm transition-colors ${
              isActive
                ? 'bg-surface2 text-text'
                : 'text-textSecondary hover:bg-surface2 hover:text-text'
            }`
          }
        >
          <Icon size={17} strokeWidth={1.75} aria-hidden="true" />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}

export default function AppShell({ children }) {
  const [mode, setMode] = useState(null)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    getHealth()
      .then((h) => setMode(h.analysis_mode))
      .catch(() => setMode(null))
  }, [])

  return (
    <div className="min-h-screen bg-bg text-text">
      {/* Desktop sidebar */}
      <div className="hidden md:flex">
        <aside className="fixed inset-y-0 left-0 flex w-60 flex-col justify-between border-r border-border bg-surface px-4 py-6">
          <div>
            <div className="mb-8 px-2">
              <span className="font-mono text-sm font-semibold tracking-tight text-text">
                FOLLOWUP
              </span>
            </div>
            <NavLinks />
          </div>
          <ModeIndicator mode={mode} />
        </aside>
        <main className="ml-60 flex-1 px-8 py-8 md:px-10 lg:px-12">
          <div className="mx-auto max-w-5xl">{children}</div>
        </main>
      </div>

      {/* Mobile top nav */}
      <div className="md:hidden">
        <header className="sticky top-0 z-20 flex items-center justify-between border-b border-border bg-surface px-4 py-3">
          <span className="font-mono text-sm font-semibold tracking-tight text-text">
            FOLLOWUP
          </span>
          <div className="flex items-center gap-3">
            <ModeIndicator mode={mode} />
            <button
              type="button"
              aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
              onClick={() => setMobileOpen((v) => !v)}
              className="rounded border border-border p-2 text-text"
            >
              {mobileOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
          </div>
        </header>
        {mobileOpen && (
          <div className="border-b border-border bg-surface px-4 py-3">
            <NavLinks onNavigate={() => setMobileOpen(false)} />
          </div>
        )}
        <main className="px-4 py-6">{children}</main>
      </div>
    </div>
  )
}
