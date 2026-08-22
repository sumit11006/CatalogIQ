import { useState } from 'react'
import { Download, FileSpreadsheet, Loader2 } from 'lucide-react'
import { api } from '../api/client'
import { Card } from '../components/ui'
import { FadeIn } from '../components/motion'
import { useRuns } from '../hooks/useCatalog'

interface PreviewRow {
  part_number: string
  product_name: string | null
  completion: number
}

export default function ExportPage() {
  const { data: runs } = useRuns()
  const [runId, setRunId] = useState('')
  const [preview, setPreview] = useState<PreviewRow[] | null>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)

  const selectedRun = (runs ?? []).find((r) => r.id === runId)

  const loadPreview = async () => {
    if (!runId) return
    setLoadingPreview(true)
    try {
      const res = await api.get(`/export/preview?run_id=${runId}&limit=5`)
      setPreview(res.data)
    } finally {
      setLoadingPreview(false)
    }
  }

  const downloadUrl = `/export/csv${runId ? `?run_id=${runId}` : ''}`

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      <FadeIn>
        <header>
          <h1 className="text-xl font-semibold">Export Delivery Format</h1>
          <p className="mt-1 text-sm text-silver-600">
            Downloads the exact UniHack delivery schema — all 252 columns in the expected order,
            ready for evaluation.
          </p>
        </header>
      </FadeIn>

      <Card>
        <div className="flex flex-wrap items-end gap-4">
          <div className="min-w-64 flex-1">
            <label className="text-xs font-medium uppercase tracking-wide text-silver-600">Dataset</label>
            <select
              value={runId}
              onChange={(e) => {
                setRunId(e.target.value)
                setPreview(null)
              }}
              className="input-precision mt-1 w-full"
            >
              <option value="">All enriched items</option>
              {(runs ?? [])
                .filter((r) => r.status === 'completed')
                .map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.filename} · {new Date(r.created_at ?? '').toLocaleString()}
                  </option>
                ))}
            </select>
          </div>

          <button onClick={loadPreview} disabled={!runId || loadingPreview} className="btn-secondary">
            {loadingPreview ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            Preview completion
          </button>

          <a href={`${api.defaults.baseURL}${downloadUrl}`} className="btn-primary">
            <Download className="h-4 w-4" />
            Download CSV
          </a>
        </div>

        {selectedRun && (
          <p className="mt-3 text-xs tabular-nums text-silver-600">
            Run contains {selectedRun.total_items} rows —{' '}
            {(selectedRun.stats?.enriched ?? 0) + (selectedRun.stats?.needs_review ?? 0)} enriched and exportable.
          </p>
        )}
      </Card>

      {preview && (
        <Card>
          <h2 className="flex items-center gap-2 text-sm font-semibold">
            <FileSpreadsheet className="h-4 w-4" /> Delivery row completeness preview
          </h2>
          <div className="mt-3 space-y-2.5">
            {preview.map((row) => (
              <div key={row.part_number} className="text-sm">
                <div className="mb-1 flex justify-between gap-3">
                  <span className="truncate font-medium">{row.product_name ?? row.part_number}</span>
                  <span className="shrink-0 tabular-nums text-silver-600">{row.completion}% of 252 cols</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-silver-200">
                  <div className="h-full rounded-full bg-gold-400" style={{ width: `${row.completion}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Card>
        <h2 className="text-sm font-semibold">What gets exported</h2>
        <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-onyx-500">
          <li>Identity: manufacturer, brand, trade name, MPN</li>
          <li>Taxonomy: Dept / Class / Fine, Classpath, UNSPSC</li>
          <li>All five description formats + marketing copy + up to 20 features</li>
          <li>Up to 50 attribute triplets with approved UOMs</li>
          <li>Raw input fields preserved for audit</li>
        </ul>
      </Card>
    </div>
  )
}
