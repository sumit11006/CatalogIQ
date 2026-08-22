export interface PipelineRun {
  id: string
  filename: string
  total_items: number
  processed_items: number
  failed_items: number
  status: 'queued' | 'running' | 'completed' | 'failed'
  stats?: { enriched?: number; needs_review?: number; failed?: number } | null
  status_counts?: Record<string, number>
  error_message?: string | null
  created_at?: string
  started_at?: string | null
  completed_at?: string | null
}

export interface ItemSummary {
  id: string
  run_id: string
  row_index: number
  mfg_part_number: string
  part_desc_raw: string
  brand_name: string | null
  manufacturer_name: string | null
  product_name: string | null
  classpath: string | null
  fine: string | null
  ai_confidence: number
  quality_score: number
  needs_review: boolean
  status: string
}

export interface RawInput {
  mfg_part_number: string
  part_desc: string
  e1_brand: string
  unilog_brand: string
  dib_brand: string
  part_manuf: string
}

export interface Attribute {
  label: string
  value: string
  uom: string
}

export interface ProvenanceEntry {
  source: 'input' | 'rule' | 'ai' | 'human'
  method?: string
  confidence: number
  reasoning?: string
}

export interface QualityCheck {
  id: string
  label: string
  passed: boolean
  detail?: string
}

export interface CatalogItemDetail {
  id: string
  run_id: string
  row_index: number
  raw_input: RawInput
  manufacturer_name: string | null
  brand_name: string | null
  trade_name: string | null
  manufacturer_part_number: string | null
  taxonomy: {
    dept: string | null
    class: string | null
    fine: string | null
    classpath: string | null
    unspsc: string | null
  }
  descriptions: {
    product_name: string | null
    short_desc: string | null
    invoice_desc: string | null
    mobile_desc: string | null
    long_desc: string | null
    retail_desc: string | null
    marketing_description: string | null
  }
  features: string[]
  attributes: Attribute[]
  applications: string | null
  includes: string | null
  standards_approvals: string | null
  provenance: Record<string, ProvenanceEntry>
  ai_confidence: number
  quality_score: number
  quality_checks: QualityCheck[]
  review_flags: string[]
  needs_review: boolean
  status: string
}

export interface ValidationQueueItem {
  id: string
  item_id: string
  run_id: string
  field_group: string
  field_name: string
  current_value: string | null
  proposed_value: string
  reason: string | null
  ai_confidence: number
  status: 'pending' | 'approved' | 'rejected'
  reviewer_note: string | null
  resolved_at: string | null
  created_at: string
  part_number: string | null
  product_name: string | null
}

export interface ValidationStats {
  total: number
  pending: number
  approved: number
  rejected: number
}

export interface DashboardData {
  items_total: number
  by_status: Record<string, number>
  avg_ai_confidence: number
  avg_quality_score: number
  needs_review_count: number
  pending_validations: number
  runs_total: number
  /** Verified by actual AI call results: live=working, ready=key set but untested,
   * fallback=AI failed and rules were used, offline=no key */
  ai_mode: 'live' | 'ready' | 'fallback' | 'offline'
  top_categories: { name: string; count: number }[]
  top_brands: { name: string; count: number }[]
}

export interface ItemsPage {
  total: number
  page: number
  page_size: number
  items: ItemSummary[]
}
