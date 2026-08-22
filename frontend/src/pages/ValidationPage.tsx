import { useState } from 'react'
import { clsx } from 'clsx'
import { Check, ChevronDown, X } from 'lucide-react'
import { ConfidenceBar, EmptyState, SourcePill } from '../components/ui'
import { FadeIn } from '../components/motion'
import { useValidationAction, useValidationQueue, useValidationStats } from '../hooks/useCatalog'

const FILTERS = [
  { key: 'pending', label: 'Pending' },
  { key: 'approved', label: 'Approved' },
  { key: 'rejected', label: 'Rejected' },
  { key: 'all', label: 'All' },
]

export default function ValidationPage() {
  const [status, setStatus] = useState('pending')
  const { data: queue, isLoading } = useValidationQueue(status)
  const { data: stats } = useValidationStats()
  const action = useValidationAction()

  return (
    <div className="space-y-5">
      <FadeIn>
        <header>
          <h1 className="text-xl font-semibold">Human-in-the-Loop Validation</h1>
          <p className="mt-1 text-sm text-silver-600">
            Low-confidence AI proposals are queued here. Approving writes the value into the live
            record and stamps provenance as human-verified.
          </p>
        </header>
      </FadeIn>

      {stats && (
        <div className="flex flex-wrap gap-3">
          <StatChip label="Total" value={stats.total} />
          <StatChip label="Pending" value={stats.pending} accent="text-amber-600" />
          <StatChip label="Approved" value={stats.approved} accent="text-gold-700" />
          <StatChip label="Rejected" value={stats.rejected} accent="text-rose-500" />
        </div>
      )}

      <div className="flex gap-1.5">
        {FILTERS.map((f) => (
          <button
            key={f.key}
            onClick={() => setStatus(f.key)}
            className={clsx(
              'rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
              status === f.key
                ? 'bg-rosegold-500 text-white shadow-sm hover:bg-rosegold-600'
                : 'bg-silver-100 text-onyx-500 hover:bg-silver-200'
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-sm text-silver-600">Loading…</p>
      ) : !queue?.length ? (
        <EmptyState
          title="Queue is clear"
          hint="Items land here when AI confidence is low or critical quality checks fail."
        />
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {queue.map((v) => (
            <QueueCard
              key={v.id}
              v={v}
              busy={action.isPending}
              onDecide={(act) => action.mutate({ id: v.id, action: act })}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function QueueCard({
  v,
  onDecide,
  busy,
}: {
  v: {
    id: string
    part_number: string | null
    product_name: string | null
    field_name: string
    field_group: string
    current_value: string | null
    proposed_value: string
    reason: string | null
    ai_confidence: number
    status: string
  }
  onDecide: (action: 'approve' | 'reject') => void
  busy: boolean
}) {
  const [open, setOpen] = useState(false)
  const resolved = v.status !== 'pending'

  return (
    <div className="panel-glass p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="mb-1 flex items-center gap-2">
            <span className="badge-glass-brand capitalize">{v.field_group}</span>
            <span className="font-mono text-xs text-silver-500">{v.part_number}</span>
          </div>
          <p className="truncate text-sm font-medium">{v.product_name ?? v.part_number}</p>
        </div>
        <button onClick={() => setOpen(!open)} className="btn-secondary !p-1.5">
          <ChevronDown className={clsx('h-4 w-4 transition-transform', open && 'rotate-180')} />
        </button>
      </div>

      {/* Diff */}
      <div className="mt-3 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1.5 rounded-lg border border-silver-200 p-3 text-sm">
        <span className="text-xs font-medium uppercase tracking-wide text-silver-500">Field</span>
        <span className="font-mono text-xs font-semibold">{v.field_name}</span>

        <span className="text-xs font-medium uppercase tracking-wide text-silver-500">Current</span>
        <span className="truncate text-silver-600 line-through decoration-silver-300">
          {v.current_value || <em className="no-underline">(empty)</em>}
        </span>

        <span className="text-xs font-medium uppercase tracking-wide text-gold-700">Proposed</span>
        <span className="break-words font-medium">{v.proposed_value}</span>
      </div>

      <div className="mt-3 flex items-center justify-between gap-3">
        <div className="w-36"><ConfidenceBar value={v.ai_confidence} /></div>

        {resolved ? (
          <span className={v.status === 'approved' ? 'badge-sage' : 'badge-coral'}>{v.status}</span>
        ) : (
          <div className="flex gap-2">
            <button disabled={busy} onClick={() => onDecide('approve')} className="btn-primary !px-3 !py-1.5 !text-xs">
              <Check className="h-3.5 w-3.5" /> Approve
            </button>
            <button disabled={busy} onClick={() => onDecide('reject')} className="btn-danger !px-3 !py-1.5 !text-xs">
              <X className="h-3.5 w-3.5" /> Reject
            </button>
          </div>
        )}
      </div>

      {open && (
        <div className="mt-3 space-y-2 border-t border-silver-100 pt-3">
          <div className="flex items-center gap-2">
            <SourcePill source="ai" />
            <span className="text-xs text-silver-600">AI rationale</span>
          </div>
          <p className="rounded-md bg-silver-50 p-2.5 text-xs italic leading-relaxed text-onyx-500">
            {v.reason || 'No rationale recorded.'}
          </p>
        </div>
      )}
    </div>
  )
}

function StatChip({ label, value, accent }: { label: string; value: number; accent?: string }) {
  return (
    <div className="panel-glass flex items-baseline gap-2 px-4 py-2.5">
      <span className={clsx('text-lg font-semibold tabular-nums', accent)}>{value}</span>
      <span className="text-xs text-silver-600">{label}</span>
    </div>
  )
}
