import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type {
  CatalogItemDetail,
  DashboardData,
  ItemsPage,
  PipelineRun,
  ValidationQueueItem,
  ValidationStats,
} from '../types/catalog'

export function useDashboard() {
  return useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => (await api.get('/analytics')).data,
    refetchInterval: 10000,
  })
}

export function useRuns() {
  return useQuery<PipelineRun[]>({
    queryKey: ['runs'],
    queryFn: async () => (await api.get('/runs')).data,
    refetchInterval: (query) =>
      query.state.data?.some((r) => r.status === 'running' || r.status === 'queued')
        ? 2000
        : false,
  })
}

export function useRun(runId?: string) {
  return useQuery<PipelineRun>({
    queryKey: ['run', runId],
    queryFn: async () => (await api.get(`/runs/${runId}`)).data,
    enabled: !!runId,
    refetchInterval: (query) =>
      query.state.data?.status === 'running' || query.state.data?.status === 'queued'
        ? 2000
        : false,
  })
}

export function useItems(runId: string | null, q: string, status: string, page: number) {
  return useQuery<ItemsPage>({
    queryKey: ['items', runId, q, status, page],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (runId) params.set('run_id', runId)
      if (q) params.set('q', q)
      if (status !== 'all') params.set('status', status)
      params.set('page', String(page))
      params.set('page_size', '25')
      return (await api.get(`/items?${params.toString()}`)).data
    },
    placeholderData: (prev) => prev,
  })
}

export function useItem(itemId: string | null) {
  return useQuery<CatalogItemDetail>({
    queryKey: ['item', itemId],
    queryFn: async () => (await api.get(`/items/${itemId}`)).data,
    enabled: !!itemId,
  })
}

export function useValidationQueue(status: string) {
  return useQuery<ValidationQueueItem[]>({
    queryKey: ['validation-queue', status],
    queryFn: async () =>
      (await api.get(`/validation/queue?status=${encodeURIComponent(status)}&limit=100`)).data,
    refetchInterval: 15000,
  })
}

export function useValidationStats() {
  return useQuery<ValidationStats>({
    queryKey: ['validation-stats'],
    queryFn: async () => (await api.get('/validation/stats')).data,
    refetchInterval: 15000,
  })
}

export function useStartSampleRun() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (limit: number) =>
      (await api.post(`/runs/sample?limit=${limit}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['runs'] }),
  })
}

export function useUploadCatalog() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ file, limit }: { file: File; limit: number }) => {
      const form = new FormData()
      form.append('file', file)
      return (
        await api.post(`/runs/upload?limit=${limit}`, form, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
      ).data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['runs'] }),
  })
}

export function useAcceptItem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (itemId: string) =>
      (await api.post(`/items/${itemId}/accept`)).data,
    onSuccess: (item: { id: string }) => {
      qc.invalidateQueries({ queryKey: ['item', item.id] })
      qc.invalidateQueries({ queryKey: ['items'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export function useValidationAction() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      id,
      action,
      note,
    }: {
      id: string
      action: 'approve' | 'reject'
      note?: string
    }) => (await api.post(`/validation/${id}/action`, { action, note })).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['validation-queue'] })
      qc.invalidateQueries({ queryKey: ['validation-stats'] })
      qc.invalidateQueries({ queryKey: ['items'] })
      qc.invalidateQueries({ queryKey: ['item'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}
