import { clsx } from 'clsx'
import { AlertTriangle, Bot, CheckCircle2, Cpu, FileText, PenLine, XCircle } from 'lucide-react'
import type { ReactNode } from 'react'

const ICON_TINTS: Record<string, string> = {
  rosegold: 'bg-rosegold-100 text-rosegold-600',
  gold: 'bg-gold-100 text-gold-700',
  silver: 'bg-silver-100 text-onyx-500',
  onyx: 'bg-onyx-700 text-white',
  amber: 'bg-[#fdf6ec] text-[#a07d33]',
  red: 'bg-red-50 text-red-500',
}

export function Card({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return <div className={clsx('panel-glass p-5', className)}>{children}</div>
}

export function StatCard({
  label,
  value,
  sub,
  icon: Icon,
  tint = 'rosegold',
  accent = 'text-onyx-700',
}: {
  label: string
  value: ReactNode
  sub?: string
  icon?: React.ComponentType<{ className?: string }>
  tint?: keyof typeof ICON_TINTS | string
  accent?: string
}) {
  return (
    <div className="panel-glass-interactive p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium uppercase tracking-wider text-silver-500">{label}</p>
          <p className={clsx('mt-1.5 text-2xl font-semibold tabular-nums', accent)}>{value}</p>
          {sub && <p className="mt-0.5 text-xs text-silver-500">{sub}</p>}
        </div>
        {Icon && (
          <div className={clsx('rounded-lg p-2', ICON_TINTS[tint] ?? ICON_TINTS.rosegold)}>
            <Icon className="h-4 w-4" />
          </div>
        )}
      </div>
    </div>
  )
}

const STATUS_STYLES: Record<string, string> = {
  pending: 'badge-glass-cyan',
  processing: 'badge-amber',
  running: 'badge-amber',
  queued: 'badge-sky',
  enriched: 'badge-sage',
  needs_review: 'badge-amber',
  approved: 'badge-sage',
  completed: 'badge-sage',
  failed: 'badge-coral',
}

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={clsx(STATUS_STYLES[status] ?? 'badge-indigo', 'capitalize')}>
      {status.replace('_', ' ')}
      {(status === 'running' || status === 'processing') && (
        <span className="pulse-dot ml-1 !h-1.5 !w-1.5" />
      )}
    </span>
  )
}

export function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = pct >= 80 ? 'bg-gold-400' : pct >= 60 ? 'bg-rosegold-400' : 'bg-red-300'
  return (
    <div className="flex items-center gap-2">
      <div className="relative h-1.5 w-full min-w-16 overflow-hidden rounded-full bg-silver-200/70">
        <div
          className={clsx('relative h-full overflow-hidden rounded-full transition-all duration-700', color)}
          style={{ width: `${pct}%` }}
        >
          {pct > 0 && <span className="bar-shimmer absolute inset-0" />}
        </div>
      </div>
      <span className="w-9 shrink-0 text-right text-xs font-medium tabular-nums text-onyx-500">
        {pct}%
      </span>
    </div>
  )
}

export function SourcePill({ source }: { source: string }) {
  const map: Record<string, { cls: string; label: string; Icon: React.ComponentType<{ className?: string }> }> = {
    ai: { cls: 'badge-violet', label: 'AI', Icon: Bot },
    rule: { cls: 'badge-sky', label: 'Rule engine', Icon: Cpu },
    input: { cls: 'badge-glass-cyan', label: 'Input', Icon: FileText },
    human: { cls: 'badge-sage', label: 'Human', Icon: PenLine },
  }
  const entry = map[source] ?? map.input
  return (
    <span className={entry.cls}>
      <entry.Icon className="h-3 w-3" />
      {entry.label}
    </span>
  )
}

export function QualityCheckRow({
  check,
}: {
  check: { id: string; label: string; passed: boolean; detail?: string }
}) {
  return (
    <div className="flex items-center justify-between gap-3 py-1.5">
      <div className="flex items-center gap-2 min-w-0">
        {check.passed ? (
          <CheckCircle2 className="h-4 w-4 shrink-0 text-gold-600" />
        ) : (
          <XCircle className="h-4 w-4 shrink-0 text-red-400" />
        )}
        <span className={clsx('truncate text-sm', check.passed && 'text-onyx-500')}>
          {check.label}
        </span>
      </div>
      {check.detail && (
        <span className="shrink-0 text-xs tabular-nums text-silver-500">{check.detail}</span>
      )}
    </div>
  )
}

export function EmptyState({
  title,
  hint,
}: {
  title: string
  hint?: string
}) {
  return (
    <div className="panel-glass flex flex-col items-center justify-center px-6 py-14 text-center">
      <div className="rounded-full bg-rosegold-100 p-3">
        <AlertTriangle className="h-5 w-5 animate-float text-rosegold-500" />
      </div>
      <p className="mt-3 font-medium text-onyx-600">{title}</p>
      {hint && <p className="mt-1 max-w-sm text-sm text-silver-500">{hint}</p>}
    </div>
  )
}
