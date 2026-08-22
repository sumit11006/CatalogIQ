import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FadeIn } from '../components/motion'
import { useDropzone } from 'react-dropzone'
import { clsx } from 'clsx'
import { FileUp, Loader2, PlayCircle, Sparkles } from 'lucide-react'
import { Card, EmptyState, StatusBadge } from '../components/ui'
import { useRuns, useStartSampleRun, useUploadCatalog } from '../hooks/useCatalog'

export default function RunsPage() {
  const { data: runs, isLoading } = useRuns()
  const sampleRun = useStartSampleRun()
  const upload = useUploadCatalog()
  const [limit, setLimit] = useState(24)
  const [dragActive, setDragActive] = useState(false)

  const { getRootProps, getInputProps } = useDropzone({
    accept: { 'text/csv': ['.csv'], 'text/plain': ['.txt'] },
    multiple: false,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
    onDrop: (files) => {
      setDragActive(false)
      if (files[0]) upload.mutate({ file: files[0], limit })
    },
  })

  return (
    <div className="space-y-6">
      <FadeIn>
        <header>
          <h1 className="text-xl font-semibold">Pipeline Runs</h1>
          <p className="mt-1 text-sm text-silver-600">
            Upload a raw catalog CSV — each row is classified, enriched, validated and made export-ready.
          </p>
        </header>
      </FadeIn>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="text-sm font-semibold">Upload Catalog CSV</h2>
          <div
            {...getRootProps()}
            className={clsx(
              'mt-3 cursor-pointer rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors',
              dragActive
                ? 'border-rosegold-400 bg-rosegold-50'
                : 'border-silver-300 hover:border-rosegold-400'
            )}
          >
            <input {...getInputProps()} />
            <FileUp className="mx-auto h-6 w-6 text-silver-500" />
            <p className="mt-2 text-sm font-medium">Drop your catalog CSV here</p>
            <p className="mt-1 text-xs text-silver-600">
              Expected columns: Mfg_Part_Num, Part_Desc, E1_Brand, Unilog_Brand, DIB_Brand, Part_Manuf
            </p>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <label className="flex items-center gap-2 text-xs text-silver-600">
              Row limit (cost control)
              <input
                type="number"
                min={1}
                max={10000}
                value={limit || ''}
                placeholder="all"
                onChange={(e) => setLimit(Number(e.target.value))}
                className="input-precision w-24 !py-1.5"
              />
            </label>
            {upload.isPending && (
              <span className="flex items-center gap-2 text-sm text-silver-600">
                <Loader2 className="h-4 w-4 animate-spin" /> Uploading…
              </span>
            )}
          </div>
          {upload.error && (
            <p className="mt-2 text-xs text-rose-600">{(upload.error as Error).message}</p>
          )}
        </Card>

        <Card className="flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-semibold">Demo Run</h2>
            <p className="mt-1.5 text-sm text-silver-600">
              Run the bundled UniHack sample dataset through the full pipeline — perfect for a live demo.
            </p>
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            {[12, 50].map((n) => (
              <button
                key={n}
                disabled={sampleRun.isPending}
                onClick={() => sampleRun.mutate(n)}
                className="btn-secondary"
              >
                <Sparkles className="h-4 w-4" />
                Sample {n} rows
              </button>
            ))}
            {sampleRun.isPending && <Loader2 className="h-4 w-4 animate-spin text-silver-500" />}
          </div>
        </Card>
      </div>

      <Card>
        <h2 className="text-sm font-semibold">All Runs</h2>
        {isLoading ? (
          <p className="py-6 text-sm text-silver-600">Loading…</p>
        ) : !runs?.length ? (
          <EmptyState title="No runs yet" hint="Upload a CSV or start the demo run above." />
        ) : (
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-silver-200 text-xs uppercase tracking-wide text-silver-600">
                  <th className="pb-2 pr-4 font-medium">File</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 pr-4 font-medium">Progress</th>
                  <th className="pb-2 pr-4 font-medium">Enriched</th>
                  <th className="pb-2 pr-4 font-medium">Review</th>
                  <th className="pb-2 pr-4 font-medium">Failed</th>
                  <th className="pb-2 font-medium">Created</th>
                  <th className="pb-2" />
                </tr>
              </thead>
              <tbody className="divide-y divide-silver-100">
                {runs.map((r) => {
                  const pct = r.total_items ? Math.round((r.processed_items / r.total_items) * 100) : 0
                  return (
                    <tr key={r.id} className="hover:bg-silver-50/60">
                      <td className="max-w-52 truncate py-2.5 pr-4 font-medium">{r.filename}</td>
                      <td className="py-2.5 pr-4"><StatusBadge status={r.status} /></td>
                      <td className="py-2.5 pr-4">
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-20 overflow-hidden rounded-full bg-silver-200">
                            <div
                              className={clsx('h-full rounded-full', r.status === 'failed' ? 'bg-rose-500' : 'bg-gold-400')}
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                          <span className="text-xs tabular-nums text-silver-600">{pct}%</span>
                        </div>
                      </td>
                      <td className="py-2.5 pr-4 tabular-nums text-gold-700">
                        {r.stats?.enriched ?? r.status_counts?.enriched ?? 0}
                      </td>
                      <td className="py-2.5 pr-4 tabular-nums text-amber-600">
                        {r.stats?.needs_review ?? r.status_counts?.needs_review ?? 0}
                      </td>
                      <td className="py-2.5 pr-4 tabular-nums text-rose-500">{r.failed_items}</td>
                      <td className="py-2.5 pr-4 text-xs tabular-nums text-silver-600">
                        {r.created_at ? new Date(r.created_at).toLocaleString() : '—'}
                      </td>
                      <td className="py-2.5 text-right">
                        <Link
                          to={`/catalog?run=${r.id}`}
                          className="inline-flex items-center gap-1.5 text-xs font-medium text-onyx-500 hover:text-onyx-800"
                        >
                          <PlayCircle className="h-3.5 w-3.5" /> Open catalog
                        </Link>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}
