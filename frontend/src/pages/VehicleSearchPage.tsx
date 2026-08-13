import React, { useState } from 'react'
import { Car, Sparkles } from 'lucide-react'
import { SearchService } from '@/services/searchService'
import { SearchResultItem } from '@/types/search'
import { formatDuration } from '@/lib/videoValidation'

export const VehicleSearchPage: React.FC = () => {
  const [query, setQuery] = useState('Black car')
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
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <Car className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-100 uppercase tracking-tight">
              Vehicle Visual Intelligence Search Console
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Search automobiles, delivery trucks, motorcycles, and vehicles across video streams
            </p>
          </div>
        </div>

        <form onSubmit={handleSearch} className="flex items-center space-x-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. 'Black car', 'White delivery truck', 'Red bicycle'"
            className="flex-1 bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 font-medium"
          />
          <button
            type="submit"
            disabled={isSearching}
            className="px-6 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg transition flex items-center space-x-2 shrink-0"
          >
            <Sparkles className="w-4 h-4" />
            <span>Find Vehicle Matches</span>
          </button>
        </form>
      </div>

      {/* Grid Results */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {results.map((item, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3 shadow-xl">
            <div className="aspect-video bg-black rounded-xl overflow-hidden">
              <img src={item.crop_url || item.image_url} alt="Vehicle Match" className="w-full h-full object-cover" />
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
