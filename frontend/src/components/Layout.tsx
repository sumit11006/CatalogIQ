import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { clsx } from 'clsx'
import { AnimatePresence, motion } from 'framer-motion'
import {
  Database,
  Download,
  LayoutDashboard,
  Menu,
  PlayCircle,
  ShieldCheck,
  Sparkles,
  X,
  Zap,
} from 'lucide-react'
import type { ReactNode } from 'react'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/runs', label: 'Pipeline Runs', icon: PlayCircle },
  { to: '/catalog', label: 'Catalog', icon: Database },
  { to: '/validation', label: 'Validation Queue', icon: ShieldCheck },
  { to: '/export', label: 'Export', icon: Download },
]

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const location = useLocation()
  return (
    <>
      <div className="flex items-center gap-3 px-5 py-6">
        <div className="rounded-xl bg-gradient-to-br from-rosegold-400 via-rosegold-500 to-gold-500 p-2 shadow-glow">
          <Zap className="h-4 w-4 text-white" />
        </div>
        <div>
          <p className="text-sm font-semibold tracking-wide text-white">CatalogIQ</p>
          <p className="text-[11px] font-medium text-silver-400">Product Intelligence v2</p>
        </div>
      </div>

      <div className="mx-5 h-px bg-gradient-to-r from-transparent via-rosegold-500/50 to-transparent" />

      <nav className="mt-4 flex-1 space-y-1 px-3">
        {NAV.map(({ to, label, icon: Icon }) => {
          const active = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
          return (
            <NavLink key={to} to={to} onClick={onNavigate} className="relative block">
              {active && (
                <motion.span
                  layoutId="nav-active"
                  className="absolute inset-0 rounded-lg bg-gradient-to-r from-rosegold-500/25 to-rosegold-500/10 ring-1 ring-inset ring-rosegold-500/30"
                  transition={{ type: 'spring', bounce: 0.18, duration: 0.55 }}
                />
              )}
              <span
                className={clsx(
                  'group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  active ? 'text-white' : 'text-silver-400 hover:text-white'
                )}
              >
                <Icon
                  className={clsx(
                    'h-4 w-4 transition-colors',
                    active ? 'text-rosegold-300' : 'text-silver-500 group-hover:text-rosegold-300'
                  )}
                />
                {label}
              </span>
            </NavLink>
          )
        })}
      </nav>

      <div className="m-3 rounded-xl border border-rosegold-500/20 bg-gradient-to-br from-onyx-800 to-onyx-900 p-3.5">
        <div className="flex items-center gap-2">
          <Sparkles className="h-3.5 w-3.5 text-gold-300" />
          <p className="text-xs font-semibold text-silver-200">UniHack Submission</p>
        </div>
        <p className="mt-1.5 text-[11px] leading-relaxed text-silver-500">
          AI catalog enrichment with traceable, human-reviewed output.
        </p>
      </div>
    </>
  )
}

export default function Layout({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="flex min-h-screen">
      {/* ── Desktop sidebar ── */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 flex-col bg-gradient-to-b from-onyx-900 via-onyx-900 to-onyx-950 shadow-[4px_0_24px_-8px_rgba(38,38,40,0.5)] lg:flex">
        <SidebarContent />
      </aside>

      {/* ── Mobile drawer ── */}
      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-black/50 backdrop-blur-[2px] lg:hidden"
              onClick={() => setOpen(false)}
            />
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 28, stiffness: 260 }}
              className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-gradient-to-b from-onyx-900 via-onyx-900 to-onyx-950 lg:hidden"
            >
              <button
                onClick={() => setOpen(false)}
                className="absolute right-3 top-4 rounded-lg p-1.5 text-silver-400 hover:bg-white/10 hover:text-white"
                aria-label="Close menu"
              >
                <X className="h-4 w-4" />
              </button>
              <SidebarContent onNavigate={() => setOpen(false)} />
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* ── Mobile top bar ── */}
      <header className="fixed inset-x-0 top-0 z-30 flex items-center gap-3 border-b border-slate-200/70 bg-white/90 px-4 py-3 backdrop-blur lg:hidden">
        <button
          onClick={() => setOpen(true)}
          className="rounded-lg border border-slate-200 p-2 text-slate-600 active:bg-slate-100"
          aria-label="Open menu"
        >
          <Menu className="h-4 w-4" />
        </button>
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-gradient-to-br from-rosegold-400 to-gold-500 p-1.5">
            <Zap className="h-3.5 w-3.5 text-white" />
          </div>
          <span className="text-sm font-semibold text-slate-800">CatalogIQ</span>
        </div>
      </header>

      {/* ── Main content ── */}
      <main className="min-w-0 flex-1 px-4 pb-20 pt-16 sm:px-6 lg:ml-60 lg:px-8 lg:pb-6 lg:pt-6">
        {children}
      </main>
    </div>
  )
}
