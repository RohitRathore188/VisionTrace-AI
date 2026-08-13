import React, { useState, useEffect, useCallback } from 'react'
import { History, Search, Image as ImageIcon, Clock, Trash2, ArrowRight, RefreshCw, AlertTriangle, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { HistoryService, HistoryEntry } from '@/services/historyService'
import { toast } from 'sonner'

function formatRelativeTime(isoStr: string | null): string {
  if (!isoStr) return '—'
  const diff = Date.now() - new Date(isoStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

function SearchTypeChip({ type }: { type: string }) {
  const isImage = type === 'image'
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium border ${
        isImage
          ? 'bg-purple-500/10 text-purple-400 border-purple-500/20'
          : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
      }`}
    >
      {isImage ? <ImageIcon className="w-3 h-3" /> : <Search className="w-3 h-3" />}
      {isImage ? 'Image' : 'Text'}
    </span>
  )
}

export const HistoryPage: React.FC = () => {
  const [items, setItems] = useState<HistoryEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [clearingAll, setClearingAll] = useState(false)

  const fetchHistory = useCallback(async (p = 1) => {
    try {
      setError(null)
      setIsLoading(true)
      const data = await HistoryService.getHistory(p, 20)
      setItems(data.items)
      setTotal(data.total)
      setPages(data.pages)
      setPage(p)
    } catch (err: any) {
      setError(err?.message || 'Failed to load search history')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchHistory(1)
  }, [fetchHistory])

  const handleDelete = async (id: string) => {
    setDeletingId(id)
    try {
      await HistoryService.deleteEntry(id)
      setItems((prev) => prev.filter((i) => i.id !== id))
      setTotal((prev) => Math.max(0, prev - 1))
      toast.success('Entry deleted')
    } catch (err: any) {
      toast.error('Failed to delete entry')
    } finally {
      setDeletingId(null)
    }
  }

  const handleClearAll = async () => {
    if (!window.confirm('Clear your entire search history? This cannot be undone.')) return
    setClearingAll(true)
    try {
      await HistoryService.clearHistory()
      setItems([])
      setTotal(0)
      toast.success('Search history cleared')
    } catch (err: any) {
      toast.error('Failed to clear history')
    } finally {
      setClearingAll(false)
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-3">
            <div className="p-2 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <History className="w-6 h-6" />
            </div>
            Search History
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            {total > 0 ? `${total} total search queries` : 'No search history yet'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchHistory(page)}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:bg-slate-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          {items.length > 0 && (
            <button
              onClick={handleClearAll}
              disabled={clearingAll}
              className="flex items-center gap-2 px-3 py-2 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-400 hover:bg-red-500/20 transition-colors disabled:opacity-50"
            >
              <Trash2 className="w-3.5 h-3.5" />
              {clearingAll ? 'Clearing…' : 'Clear All'}
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Loading skeleton */}
      {isLoading && (
        <div className="space-y-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-20 rounded-2xl bg-slate-900/60 border border-slate-800 animate-pulse" />
          ))}
        </div>
      )}

      {/* History list */}
      {!isLoading && items.length > 0 && (
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              className="group flex items-center gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 px-5 py-4 hover:border-slate-700 hover:bg-slate-900/80 transition-all"
            >
              {/* Type icon */}
              <div
                className={`p-2.5 rounded-xl shrink-0 ${
                  item.search_type === 'image'
                    ? 'bg-purple-500/10 border border-purple-500/20'
                    : 'bg-blue-500/10 border border-blue-500/20'
                }`}
              >
                {item.search_type === 'image' ? (
                  <ImageIcon className="w-5 h-5 text-purple-400" />
                ) : (
                  <Search className="w-5 h-5 text-blue-400" />
                )}
              </div>

              {/* Query */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <SearchTypeChip type={item.search_type} />
                  <span className="text-xs text-slate-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {formatRelativeTime(item.created_at)}
                  </span>
                </div>
                <p className="text-sm font-medium text-slate-200 truncate">
                  {item.query_text || 'Visual similarity search'}
                </p>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-xs text-slate-500">
                    {item.result_count} results found
                  </span>
                  <span className="text-slate-700">·</span>
                  <span className="text-xs text-slate-500">
                    {item.execution_time_ms.toFixed(1)}ms
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                <Link
                  to={`/search?q=${encodeURIComponent(item.query_text || '')}&type=${item.search_type}`}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-400 hover:bg-indigo-500/20 transition-colors"
                >
                  <ArrowRight className="w-3 h-3" />
                  Re-run
                </Link>
                <button
                  onClick={() => handleDelete(item.id)}
                  disabled={deletingId === item.id}
                  className="p-1.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition-colors disabled:opacity-50"
                >
                  {deletingId === item.id ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <X className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && items.length === 0 && !error && (
        <div className="flex flex-col items-center justify-center py-24 rounded-2xl border border-dashed border-slate-800 text-slate-500">
          <History className="w-12 h-12 mb-3 opacity-20" />
          <p className="text-sm font-medium">No search history yet</p>
          <p className="text-xs mt-1 text-slate-600">
            Run a text or image search to start building history
          </p>
          <Link
            to="/search"
            className="mt-4 flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-sm text-indigo-400 hover:bg-indigo-500/20 transition-colors"
          >
            <Search className="w-4 h-4" />
            Go to Search
          </Link>
        </div>
      )}

      {/* Pagination */}
      {!isLoading && pages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <button
            onClick={() => fetchHistory(page - 1)}
            disabled={page <= 1}
            className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 disabled:opacity-40 hover:bg-slate-700 transition-colors"
          >
            ← Previous
          </button>
          <span className="text-xs text-slate-500">
            Page {page} of {pages}
          </span>
          <button
            onClick={() => fetchHistory(page + 1)}
            disabled={page >= pages}
            className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 disabled:opacity-40 hover:bg-slate-700 transition-colors"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}
