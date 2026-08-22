import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { clsx } from 'clsx'
import { ChevronLeft, ChevronRight, Search, X } from 'lucide-react'
import { FadeIn } from '../components/motion'
import {
  ConfidenceBar,
  EmptyState,
  QualityCheckRow,
  SourcePill,
  StatusBadge,
} from '../components/ui'
import { useItem, useItems, useRuns, useAcceptItem } from '../hooks/useCatalog'
import type { CatalogItemDetail } from '../types/catalog'

const STATUS_FILTERS = ['all', 'enriched', 'needs_review', 'pending', 'failed']

export default function CatalogPage() {
  const [params, setParams] = useSearchParams()
  const runId = params.get('run') ?? ''
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('all')
  const [page, setPage] = useState(1)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const { data: runs } = useRuns()
  const { data, isLoading } = useItems(runId || null, q, status, page)
  const { data: item } = useItem(selectedId)

  const totalPages = useMemo(
    () => Math.max(1, Math.ceil((data?.total ?? 0) / (data?.page_size ?? 25))),
    [data]
  )

  return (
    <div className="space-y-5">
      <FadeIn>
        <header className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-xl font-semibold">Enriched Catalog</h1>
            <p className="mt-1 text-sm text-silver-600">
              Every row with its full delivery-ready record, provenance and quality score.
            </p>
          </div>
        <select
          value={runId}
          onChange={(e) => {
            setPage(1)
            if (e.target.value) setParams({ run: e.target.value })
            else setParams({})
          }}
          className="input-precision w-64"
        >
          <option value="">All runs</option>
          {(runs ?? []).map((r) => (
            <option key={r.id} value={r.id}>
              {r.filename} · {new Date(r.created_at ?? '').toLocaleString()}
            </option>
          ))}
        </select>
        </header>
      </FadeIn>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative w-72">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-silver-500" />
          <input
            value={q}
            onChange={(e) => {
              setQ(e.target.value)
              setPage(1)
            }}
            placeholder="Search part number, brand, title…"
            className="input-precision pl-9"
          />
        </div>
        <div className="flex gap-1.5">
          {STATUS_FILTERS.map((s) => (
            <button
              key={s}
              onClick={() => {
                setStatus(s)
                setPage(1)
              }}
              className={clsx(
                'rounded-lg px-3 py-1.5 text-xs font-medium capitalize transition-colors',
                status === s
                  ? 'bg-rosegold-500 text-white shadow-sm hover:bg-rosegold-600'
                  : 'bg-silver-100 text-onyx-500 hover:bg-silver-200'
              )}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {!data?.items.length && !isLoading ? (
        <EmptyState title="No catalog items" hint="Start a pipeline run first." />
      ) : (
        <div className="panel-glass overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-silver-200 text-xs uppercase tracking-wide text-silver-600">
                <th className="px-4 py-3 font-medium">#</th>
                <th className="px-4 py-3 font-medium">MPN</th>
                <th className="px-4 py-3 font-medium">Raw Description</th>
                <th className="px-4 py-3 font-medium">Product Title</th>
                <th className="px-4 py-3 font-medium">Brand</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
                <th className="px-4 py-3 font-medium">Quality</th>
                <th className="px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-silver-100">
              {isLoading && (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-sm text-silver-600">
                    Loading…
                  </td>
                </tr>
              )}
              {data?.items.map((it) => (
                <tr
                  key={it.id}
                  onClick={() => setSelectedId(it.id)}
                  className="cursor-pointer hover:bg-silver-50/70"
                >
                  <td className="px-4 py-2.5 tabular-nums text-silver-500">{it.row_index + 1}</td>
                  <td className="max-w-36 truncate px-4 py-2.5 font-mono text-xs">{it.mfg_part_number}</td>
                  <td className="max-w-56 truncate px-4 py-2.5 text-silver-600">{it.part_desc_raw}</td>
                  <td className="max-w-72 truncate px-4 py-2.5 font-medium">{it.product_name ?? '—'}</td>
                  <td className="px-4 py-2.5">{it.brand_name || <span className="text-silver-500">—</span>}</td>
                  <td className="w-32 px-4 py-2.5"><ConfidenceBar value={it.ai_confidence} /></td>
                  <td className="px-4 py-2.5 tabular-nums font-medium">{it.quality_score || '—'}</td>
                  <td className="px-4 py-2.5"><StatusBadge status={it.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="flex items-center justify-between border-t border-silver-100 px-4 py-3 text-xs text-silver-600">
            <span className="tabular-nums">
              {data?.total ?? 0} items · page {page} of {totalPages}
            </span>
            <div className="flex gap-1.5">
              <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1} className="btn-secondary !p-2 disabled:opacity-40">
                <ChevronLeft className="h-3.5 w-3.5" />
              </button>
              <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages} className="btn-secondary !p-2 disabled:opacity-40">
                <ChevronRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {selectedId && (
        <ItemDrawer item={item} onClose={() => setSelectedId(null)} />
      )}
    </div>
  )
}

function ItemDrawer({
  item,
  onClose,
}: {
  item?: CatalogItemDetail
  onClose: () => void
}) {
  const [tab, setTab] = useState<'record' | 'attributes' | 'trace' | 'quality'>('record')
  const accept = useAcceptItem()

  return (
    <div className="fixed inset-0 z-30 flex justify-end bg-black/30 backdrop-blur-[2px]" onClick={onClose}>
      <div
        onClick={(e) => e.stopPropagation()}
        className="h-full w-full max-w-3xl overflow-y-auto border-l border-silver-200 bg-white shadow-2xl"
      >
        {!item ? (
          <div className="p-6 text-sm text-silver-600">Loading…</div>
        ) : (
          <>
            <div className="sticky top-0 z-10 flex items-start justify-between gap-4 border-b border-silver-200 bg-white/95 px-4 py-4 backdrop-blur sm:px-6">
              <div className="min-w-0">
                <div className="mb-1 flex items-center gap-2">
                  <StatusBadge status={item.status} />
                  <span className="font-mono text-xs text-silver-500">{item.raw_input.mfg_part_number}</span>
                </div>
                <h2 className="truncate text-base font-semibold">{item.descriptions.product_name ?? 'Untitled'}</h2>
                <p className="mt-0.5 truncate text-xs text-silver-500">{item.taxonomy.classpath}</p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                {item.needs_review && (
                  <button
                    onClick={() => accept.mutate(item.id)}
                    disabled={accept.isPending}
                    className="btn-success !px-3 !py-1.5 !text-xs"
                  >
                    Accept record
                  </button>
                )}
                <button onClick={onClose} className="btn-secondary !p-2">
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div className="flex flex-wrap gap-1 px-4 pt-3 sm:px-6">
              {([
                ['record', 'Record'],
                ['attributes', `Attributes (${item.attributes.length})`],
                ['trace', 'Traceability'],
                ['quality', `Quality (${item.quality_score})`],
              ] as const).map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setTab(key)}
                  className={clsx(
                    'rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                    tab === key
                      ? 'bg-rosegold-500 text-white shadow-sm hover:bg-rosegold-600'
                      : 'text-silver-600 hover:text-onyx-700'
                  )}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="space-y-5 p-4 sm:p-6">
              {tab === 'record' && (
                <>
                  <Section title="Descriptions — five formats from one source">
                    {Object.entries(item.descriptions).map(([k, v]) =>
                      v ? (
                        <Field key={k} label={DESC_LABELS[k] ?? k} value={v} hint={`${v.length} chars`} />
                      ) : null
                    )}
                  </Section>
                  <Section title="Identity & Taxonomy">
                    <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm">
                      <KV k="Manufacturer" v={item.manufacturer_name} />
                      <KV k="Brand" v={item.brand_name} />
                      <KV k="Trade name" v={item.trade_name} />
                      <KV k="UNSPSC" v={item.taxonomy.unspsc} />
                      <KV k="Dept / Class / Fine" v={[item.taxonomy.dept, item.taxonomy.class, item.taxonomy.fine].filter(Boolean).join(' › ')} />
                    </div>
                  </Section>
                  {item.features.length > 0 && (
                    <Section title="Features">
                      <ul className="list-inside list-disc space-y-1 text-sm text-onyx-600">
                        {item.features.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </Section>
                  )}
                </>
              )}

              {tab === 'attributes' && (
                <Section title="Extracted attributes (label · value · approved UOM)">
                  {item.attributes.length === 0 ? (
                    <p className="text-sm text-silver-600">No attributes extracted.</p>
                  ) : (
                    <table className="w-full text-left text-sm">
                      <thead>
                        <tr className="text-xs uppercase tracking-wide text-silver-500">
                          <th className="pb-2 font-medium">Label</th>
                          <th className="pb-2 font-medium">Value</th>
                          <th className="pb-2 font-medium">UOM</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-silver-100">
                        {item.attributes.map((a, i) => (
                          <tr key={i}>
                            <td className="py-1.5 pr-4">{a.label}</td>
                            <td className="py-1.5 pr-4 font-medium">{a.value}</td>
                            <td className="py-1.5">
                              {a.uom ? (
                                <span className="badge-glass-brand">{a.uom}</span>
                              ) : (
                                <span className="text-silver-400">—</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </Section>
              )}

              {tab === 'trace' && (
                <Section title="Field-level provenance">
                  <p className="-mt-2 mb-3 text-xs text-silver-600">
                    Every generated field records where its value came from, how, and with what confidence.
                  </p>
                  <div className="space-y-2">
                    {Object.entries(item.provenance).map(([field, p]) => (
                      <div key={field} className="rounded-lg border border-silver-200 p-3 text-sm">
                        <div className="flex items-center justify-between gap-3">
                          <div className="flex items-center gap-2">
                            <SourcePill source={p.source} />
                            <span className="font-mono text-xs font-semibold">{field}</span>
                          </div>
                          <ConfidenceBar value={p.confidence ?? 0} />
                        </div>
                        {p.method && <p className="mt-1.5 text-xs text-silver-600">{p.method}</p>}
                        {p.reasoning && (
                          <p className="mt-1 rounded-md bg-silver-50 p-2 text-xs italic leading-relaxed text-onyx-500">
                            “{p.reasoning}”
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </Section>
              )}

              {tab === 'quality' && (
                <>
                  <div className="grid grid-cols-3 gap-3">
                    <Stat label="AI confidence" value={`${Math.round(item.ai_confidence * 100)}%`} />
                    <Stat label="Quality score" value={`${item.quality_score}`} />
                    <Stat label="Review flags" value={`${item.review_flags.length}`} />
                  </div>
                  <Section title="Content-standard compliance checks">
                    {item.quality_checks.map((c) => (
                      <QualityCheckRow key={c.id} check={c} />
                    ))}
                  </Section>
                  <Section title="Raw input vs enriched">
                    <div className="space-y-1 text-sm">
                      {Object.entries(item.raw_input).map(([k, v]) => (
                        <KV key={k} k={RAW_LABELS[k] ?? k} v={v} muted />
                      ))}
                    </div>
                  </Section>
                </>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

const DESC_LABELS: Record<string, string> = {
  product_name: 'Product Title',
  short_desc: 'Short Description',
  invoice_desc: 'Invoice Desc (≤40 CAPS)',
  mobile_desc: 'Mobile Desc (60–80 chars)',
  long_desc: 'Long Description',
  retail_desc: 'Retail Desc',
  marketing_description: 'Marketing Copy',
}

const RAW_LABELS: Record<string, string> = {
  mfg_part_number: 'MPN',
  part_desc: 'Part description',
  e1_brand: 'E1 Brand',
  unilog_brand: 'Unilog Brand',
  dib_brand: 'DIB Brand',
  part_manuf: 'Part manufacturer',
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-silver-600">{title}</h3>
      <div className="space-y-2">{children}</div>
    </section>
  )
}

function Field({ label, value, hint }: { label: string; value: string; hint?: string }) {
  const caps = label.includes('CAPS')
  return (
    <div className="rounded-lg border border-silver-200 p-3">
      <div className="flex items-center justify-between gap-2">
        <p className="text-[11px] font-medium uppercase tracking-wide text-silver-600">{label}</p>
        {hint && <span className="text-[11px] tabular-nums text-silver-500">{hint}</span>}
      </div>
      <p className={clsx('mt-1 text-sm leading-relaxed', caps && 'font-mono text-xs tracking-wide')}>
        {value}
      </p>
    </div>
  )
}

function KV({ k, v, muted }: { k: string; v?: string | null; muted?: boolean }) {
  return (
    <div className="flex justify-between gap-3 border-b border-silver-100 py-1">
      <span className="shrink-0 text-xs text-silver-600">{k}</span>
      <span className={clsx('truncate text-right', muted ? 'text-silver-600' : 'font-medium')}>{v || '—'}</span>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-silver-100 p-3 text-center">
      <p className="text-lg font-semibold tabular-nums">{value}</p>
      <p className="text-[11px] text-silver-600">{label}</p>
    </div>
  )
}
