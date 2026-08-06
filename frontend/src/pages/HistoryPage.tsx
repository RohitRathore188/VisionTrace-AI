import React, { useState } from 'react'
import { History, Search, Image as ImageIcon, Clock, Trash2, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

interface HistoryEntry {
  id: string
  query_text?: string
  query_type: 'text' | 'image'
  results_count: number
  latency_ms: number
  created_at: string
  top_score: number
}

const MOCK_HISTORY: HistoryEntry[] = [
  {
    id: 'hist-001',
    query_text: 'red car parked near building entrance',
    query_type: 'text',
    results_count: 5,
    latency_ms: 18.4,
    created_at: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    top_score: 0.892,
  },
  {
    id: 'hist-002',
    query_text: 'person wearing black jacket and backpack',
    query_type: 'text',
    results_count: 12,
    latency_ms: 24.1,
    created_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    top_score: 0.941,
  },
  {
    id: 'hist-003',
    query_text: 'visual_search_cropped_frame_04.jpg',
    query_type: 'image',
    results_count: 8,
    latency_ms: 32.7,
    created_at: new Date(Date.now() - 1000 * 60 * 360).toISOString(),
    top_score: 0.876,
  },
]

export const HistoryPage: React.FC = () => {
  const [historyItems, setHistoryItems] = useState<HistoryEntry[]>(MOCK_HISTORY)

  const handleClearHistory = () => {
    if (window.confirm('Clear all search query logs?')) {
      setHistoryItems([])
    }
  }

  const handleDeleteEntry = (id: string) => {
    setHistoryItems((prev) => prev.filter((item) => item.id !== id))
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight flex items-center space-x-3">
            <div className="p-2 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <History className="w-6 h-6" />
            </div>
            <span>Search & Query History Logs</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Review past natural language text queries, visual similarity searches, and FAISS latency benchmarks
          </p>
        </div>

        {historyItems.length > 0 && (
          <button
            onClick={handleClearHistory}
            className="flex items-center space-x-2 text-xs font-semibold px-3.5 py-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 transition self-start sm:self-auto"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear History Log</span>
          </button>
        )}
      </div>

      {/* History Items Container */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6">
        {historyItems.length === 0 ? (
          <div className="py-16 border-2 border-dashed border-slate-800 rounded-2xl text-center space-y-3">
            <Clock className="w-12 h-12 text-slate-600 mx-auto" />
            <p className="text-slate-300 text-base font-bold">No search history recorded</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Run text-to-video or image-to-video similarity searches in FAISS Search to populate history logs.
            </p>
            <Link
              to="/search"
              className="inline-flex items-center space-x-2 mt-2 px-4 py-2 rounded-xl text-xs font-bold bg-amber-600 text-white hover:bg-amber-500 transition"
            >
              <span>Go to FAISS Search</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {historyItems.map((item) => (
              <div
                key={item.id}
                className="flex flex-col md:flex-row md:items-center justify-between p-4 bg-slate-950 border border-slate-800 hover:border-slate-700 rounded-2xl transition gap-4"
              >
                <div className="flex items-start space-x-3.5 min-w-0">
                  <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-amber-400 shrink-0 mt-0.5">
                    {item.query_type === 'text' ? <Search className="w-5 h-5" /> : <ImageIcon className="w-5 h-5" />}
                  </div>
                  <div className="min-w-0 space-y-1">
                    <p className="text-base font-bold text-slate-200 truncate">{item.query_text}</p>
                    <div className="flex items-center space-x-3 text-xs text-slate-400 font-mono">
                      <span className="capitalize font-semibold text-amber-400/90">{item.query_type} Query</span>
                      <span>•</span>
                      <span>Latency: {item.latency_ms.toFixed(1)} ms</span>
                      <span>•</span>
                      <span>Matches: {item.results_count} keyframes</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4 self-end md:self-center shrink-0">
                  <div className="text-right">
                    <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold block">
                      Top Similarity Score
                    </span>
                    <span className="text-sm font-bold text-emerald-400 font-mono">
                      {(item.top_score * 100).toFixed(1)}% Match
                    </span>
                  </div>

                  <button
                    onClick={() => handleDeleteEntry(item.id)}
                    className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition"
                    title="Delete Entry"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
