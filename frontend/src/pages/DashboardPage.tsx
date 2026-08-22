import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { ArrowRight, Bot, BotOff, Database, PlayCircle, ShieldCheck, Sparkles, Star } from 'lucide-react'
import { Card, EmptyState, StatCard } from '../components/ui'
import { CountUp, FadeIn, Stagger, StaggerItem } from '../components/motion'
import { useDashboard, useRuns } from '../hooks/useCatalog'
import type { PipelineRun } from '../types/catalog'

const STATUS_COLORS: Record<string, string> = {
  enriched: '#c9a97e',
  needs_review: '#dfbcae',
  pending: '#c3c3c6',
  failed: '#d98a80',
}

export default function DashboardPage() {
  const { data } = useDashboard()
  const { data: runs } = useRuns()

  if (!data) return null

  const statusData = Object.entries(data.by_status).map(([name, value]) => ({
    name: name.replace('_', ' '),
    value,
  }))
  const recentRuns = (runs ?? []).slice(0, 5)
  const exportable = (data.by_status.enriched ?? 0) + (data.by_status.needs_review ?? 0)

  return (
    <div className="space-y-6">
      {/* ── Hero ── */}
      <FadeIn>
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-onyx-800 via-onyx-900 to-onyx-950 p-5 shadow-lift sm:p-8">
          {/* decorative glows */}
          <div className="pointer-events-none absolute -right-16 -top-24 h-72 w-72 rounded-full bg-rosegold-500/25 blur-[90px]" />
          <div className="pointer-events-none absolute -bottom-28 left-1/3 h-64 w-64 rounded-full bg-gold-400/20 blur-[90px]" />

          <div className="relative flex flex-wrap items-center justify-between gap-8">
            <div className="max-w-xl">
              <span className="badge-violet !bg-white/10 !text-gold-300 !border-gold-400/30">
                <Sparkles className="h-3 w-3" />
                AI-Powered Product Intelligence
              </span>
              <motion.h1
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1, duration: 0.5 }}
                className="mt-4 text-2xl font-semibold leading-snug text-white"
              >
                From cryptic catalog rows to{' '}
                <span className="bg-gradient-to-r from-rosegold-300 to-gold-300 bg-clip-text text-transparent">
                  commerce-ready records
                </span>
              </motion.h1>
              <p className="mt-2.5 text-sm leading-relaxed text-silver-300">
                Classification, brand resolution, five description formats, attribute extraction and
                human-in-the-loop validation — every field traceable to its source.
              </p>
              <div className="mt-5 flex flex-wrap gap-3">
                <Link to="/runs" className="btn-primary shadow-glow">
                  <PlayCircle className="h-4 w-4" />
                  New Enrichment Run
                </Link>
                <Link
                  to="/catalog"
                  className="inline-flex items-center gap-2 rounded-lg border border-white/15 px-4 py-2 text-sm font-medium text-silver-200 transition-colors hover:border-rosegold-400/50 hover:text-white"
                >
                  Browse catalog
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>

            {/* floating stat chips */}
            <div className="hidden flex-col gap-3 lg:flex">
              {[
                { label: 'Items processed', value: data.items_total, tint: 'text-rosegold-300' },
                { label: 'Export-ready', value: exportable, tint: 'text-gold-300' },
                {
                  label: 'Avg quality score',
                  value: `${data.avg_quality_score}`,
                  tint: 'text-silver-200',
                },
              ].map((chip, i) => (
                <motion.div
                  key={chip.label}
                  initial={{ opacity: 0, x: 24 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.25 + i * 0.12, duration: 0.5 }}
                  className="flex items-center gap-4 rounded-xl border border-white/10 bg-white/[0.06] px-5 py-3 backdrop-blur-sm"
                >
                  <span className={`text-xl font-semibold tabular-nums ${chip.tint}`}>
                    <CountUp value={chip.value} />
                  </span>
                  <span className="text-xs font-medium uppercase tracking-wider text-silver-400">
                    {chip.label}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </FadeIn>

      {/* ── KPI cards ── */}
      <Stagger className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:gap-4 lg:grid-cols-5">
        <StaggerItem>
          <StatCard label="Items Processed" value={<CountUp value={data.items_total} />} icon={Database} tint="rosegold" />
        </StaggerItem>
        <StaggerItem>
          <StatCard
            label="Avg AI Confidence"
            value={<CountUp value={Math.round(data.avg_ai_confidence * 100)} suffix="%" />}
            icon={Sparkles}
            tint="gold"
          />
        </StaggerItem>
        <StaggerItem>
          <StatCard
            label="Avg Quality Score"
            value={<CountUp value={data.avg_quality_score} decimals={1} />}
            sub="content-standard compliance"
            icon={Star}
            tint="silver"
          />
        </StaggerItem>
        <StaggerItem>
          <StatCard
            label="Awaiting Review"
            value={<CountUp value={data.pending_validations} />}
            accent={data.pending_validations > 0 ? 'text-rosegold-600' : undefined}
            icon={ShieldCheck}
            tint="amber"
          />
        </StaggerItem>
        <StaggerItem>
          <StatCard
            label="Gemini Engine"
            value={
              data.ai_mode === 'live' ? (
                <span className="flex items-center gap-2 text-gold-700">
                  Live <span className="pulse-dot" />
                </span>
              ) : data.ai_mode === 'ready' ? (
                <span className="text-onyx-500">Ready</span>
              ) : (
                <span className="text-rosegold-600">Fallback</span>
              )
            }
            sub={
              data.ai_mode === 'live'
                ? 'API verified working'
                : data.ai_mode === 'ready'
                  ? 'key set — unverified'
                  : 'rules-based mode'
            }
            icon={data.ai_mode === 'live' ? Bot : BotOff}
            tint={data.ai_mode === 'live' ? 'gold' : data.ai_mode === 'ready' ? 'silver' : 'amber'}
          />
        </StaggerItem>
      </Stagger>

      {(data.ai_mode === 'fallback' || data.ai_mode === 'offline') && (
        <FadeIn delay={0.1}>
          <div className="flex items-start gap-3 rounded-xl border border-[#f0dfc0] bg-[#fdf6ec] px-4 py-3">
            <BotOff className="mt-0.5 h-4 w-4 shrink-0 text-[#a07d33]" />
            <p className="text-sm leading-relaxed text-[#8a6d2c]">
              <strong>Gemini unavailable</strong> — recent results came from the deterministic
              rules fallback (lower confidence, keyword classification). Add a valid{' '}
              <code className="rounded bg-white/70 px-1.5 py-0.5 font-mono text-xs">GEMINI_API_KEY</code>{' '}
              in <code className="rounded bg-white/70 px-1.5 py-0.5 font-mono text-xs">backend/.env</code>{' '}
              and re-run for full AI enrichment.
            </p>
          </div>
        </FadeIn>
      )}

      {/* ── Charts ── */}
      <div className="grid gap-4 lg:grid-cols-3">
        <FadeIn delay={0.15} className="lg:col-span-2">
          <Card className="h-full">
            <h2 className="text-sm font-semibold">Top Categories (Dept level)</h2>
            {data.top_categories.length === 0 ? (
              <EmptyState title="No enriched items yet" hint="Start a pipeline run to populate the catalog." />
            ) : (
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.top_categories} margin={{ top: 8, right: 8, left: -18, bottom: 24 }}>
                    <CartesianGrid strokeDasharray="4 4" stroke="rgba(142, 142, 144, 0.2)" vertical={false} />
                    <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#8e8e90' }} angle={-20} textAnchor="end" interval={0} />
                    <YAxis tick={{ fontSize: 11, fill: '#8e8e90' }} allowDecimals={false} />
                    <Tooltip cursor={{ fill: 'rgba(189, 140, 125, 0.08)' }} wrapperClassName="!text-xs !rounded-lg" />
                    <Bar dataKey="count" fill="#bd8c7d" radius={[6, 6, 0, 0]} maxBarSize={56} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </Card>
        </FadeIn>

        <FadeIn delay={0.22}>
          <Card className="h-full">
            <h2 className="text-sm font-semibold">Pipeline Status Mix</h2>
            {statusData.length === 0 ? (
              <p className="mt-4 text-sm text-silver-500">No data yet.</p>
            ) : (
              <div className="mt-2 h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={statusData} dataKey="value" nameKey="name" innerRadius={52} outerRadius={82} paddingAngle={4} cornerRadius={6}>
                      {statusData.map((entry) => (
                        <Cell key={entry.name} fill={STATUS_COLORS[entry.name.replace(' ', '_')] ?? '#c3c3c6'} />
                      ))}
                    </Pie>
                    <Tooltip wrapperClassName="!text-xs !rounded-lg" />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
            <div className="mt-1 space-y-1.5">
              {statusData.map((s) => (
                <div key={s.name} className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-2 capitalize text-onyx-500">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{ background: STATUS_COLORS[s.name.replace(' ', '_')] ?? '#c3c3c6' }}
                    />
                    {s.name}
                  </span>
                  <span className="font-medium tabular-nums">{s.value}</span>
                </div>
              ))}
            </div>
          </Card>
        </FadeIn>
      </div>

      {/* ── Bottom row ── */}
      <div className="grid gap-4 lg:grid-cols-3">
        <FadeIn delay={0.28} className="lg:col-span-2">
          <Card className="h-full">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold">Recent Runs</h2>
              <Link to="/runs" className="text-xs font-medium text-rosegold-600 hover:text-rosegold-700 hover:underline">
                View all →
              </Link>
            </div>
            <div className="mt-3 divide-y divide-silver-100">
              {recentRuns.length === 0 && (
                <p className="py-6 text-sm text-silver-500">No runs yet — upload a catalog CSV to begin.</p>
              )}
              {recentRuns.map((r: PipelineRun) => (
                <div key={r.id} className="flex items-center justify-between gap-3 py-2.5">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{r.filename}</p>
                    <p className="text-xs tabular-nums text-silver-500">
                      {r.processed_items}/{r.total_items} items · {new Date(r.created_at ?? '').toLocaleString()}
                    </p>
                  </div>
                  <span className={r.status === 'completed' ? 'badge-sage' : r.status === 'failed' ? 'badge-coral' : 'badge-amber'}>
                    {r.status}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </FadeIn>

        <FadeIn delay={0.34}>
          <Card className="h-full">
            <h2 className="text-sm font-semibold">Top Brands Detected</h2>
            <div className="mt-3 space-y-2">
              {data.top_brands.length === 0 && (
                <p className="text-sm text-silver-500">No brands resolved yet.</p>
              )}
              {data.top_brands.map((b, i) => (
                <div key={b.name} className="flex items-center justify-between gap-3 text-sm">
                  <span className="flex min-w-0 items-center gap-2.5">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-rosegold-100 text-[11px] font-bold text-rosegold-600">
                      {i + 1}
                    </span>
                    <span className="truncate">{b.name}</span>
                  </span>
                  <span className="badge-glass-cyan tabular-nums">{b.count}</span>
                </div>
              ))}
            </div>
          </Card>
        </FadeIn>
      </div>
    </div>
  )
}
