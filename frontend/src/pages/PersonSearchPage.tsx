import React, { useState } from 'react'
import { UserCheck, Sparkles, AlertCircle } from 'lucide-react'
import { SearchService } from '@/services/searchService'
import { SearchResultItem } from '@/types/search'
import { formatDuration } from '@/lib/videoValidation'

export const PersonSearchPage: React.FC = () => {
  const [query, setQuery] = useState('Person wearing black shirt')
  const [results, setResults] = useState<SearchResultItem[]>([])
  const [isSearching, setIsSearching] = useState(false)

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    setIsSearching(true)
    try {
      const res = await SearchService.searchByText(query, 12)
      setResults(res.results || [])
    } catch (err) {
      console.error(err)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Disclaimer Alert */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 flex items-center space-x-3 text-amber-300 text-xs">
        <AlertCircle className="w-5 h-5 shrink-0 text-amber-400" />
        <div>
          <strong className="font-bold uppercase tracking-wider block">AI Disclaimer: Visual Similarity Match</strong>
          This tool provides visual attribute similarity results for personnel review. It does not perform facial recognition or establish verified personal identity.
        </div>
      </div>

      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <UserCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-100 uppercase tracking-tight">
              Person Visual Similarity Search Console
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Query clothing, attributes, and visual characteristics across surveillance keyframes
            </p>
          </div>
        </div>

        <form onSubmit={handleSearch} className="flex items-center space-x-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. 'Person wearing black shirt', 'Person carrying backpack'"
            className="flex-1 bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 font-medium"
          />
          <button
            type="submit"
            disabled={isSearching}
            className="px-6 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg transition flex items-center space-x-2 shrink-0"
          >
            <Sparkles className="w-4 h-4" />
            <span>Find Person Matches</span>
          </button>
        </form>
      </div>

      {/* Grid Results */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {results.map((item, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3 shadow-xl">
            <div className="aspect-video bg-black rounded-xl overflow-hidden">
              <img src={item.crop_url || item.image_url} alt="Person Match" className="w-full h-full object-cover" />
            </div>

            <div>
              <h4 className="font-bold text-slate-100 text-xs truncate">{item.video_title}</h4>
              <p className="text-[11px] font-mono text-emerald-400 font-bold mt-1">
                {(item.similarity_score * 100).toFixed(1)}% Visual Match
              </p>
              <p className="text-[11px] font-mono text-slate-400">@ {formatDuration(item.timestamp_seconds)} (Frame #{item.frame_number})</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
