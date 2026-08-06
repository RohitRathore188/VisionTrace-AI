import React, { useState, useEffect, useCallback, useRef } from 'react'
import { SearchService } from '@/services/searchService'
import { SearchResultItem, SearchResponse } from '@/types/search'
import { InteractiveVideoTimeline } from '@/components/search/InteractiveVideoTimeline'
import { formatDuration } from '@/lib/videoValidation'
import {
  Search as SearchIcon,
  Sparkles,
  Zap,
  Clock,
  Film,
  Sliders,
  CheckCircle2,
  Upload,
  Image as ImageIcon,
  RefreshCw,
  X,
  Crosshair,
  UserCheck,
  Briefcase,
  Car,
  Bike,
  Activity,
} from 'lucide-react'

// Natural language surveillance search examples requested by user
const NATURAL_LANGUAGE_EXAMPLES = [
  { label: 'Person wearing white shirt', icon: UserCheck, query: 'Person wearing white shirt' },
  { label: 'Blue backpack', icon: Briefcase, query: 'Blue backpack' },
  { label: 'Black car', icon: Car, query: 'Black car' },
  { label: 'Red bicycle', icon: Bike, query: 'Red bicycle' },
  { label: 'Person carrying black backpack', icon: UserCheck, query: 'Person carrying black backpack' },
  { label: 'White delivery truck', icon: Car, query: 'White delivery truck' },
]

export const SearchPage: React.FC = () => {
  const [searchMode, setSearchMode] = useState<'text' | 'image'>('text')
  const [queryText, setQueryText] = useState<string>('Person wearing white shirt')
  const [queryImage, setQueryImage] = useState<File | null>(null)
  const [queryImagePreview, setQueryImagePreview] = useState<string | null>(null)

  const [topK, setTopK] = useState<number>(12)
  const [minScore, _setMinScore] = useState<number>(0.15)
  const [isSearching, setIsSearching] = useState<boolean>(false)
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null)
  const [selectedResult, setSelectedResult] = useState<SearchResultItem | null>(null)
  const [_indexStats, setIndexStats] = useState<any>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'timeline'>('timeline')

  const imageInputRef = useRef<HTMLInputElement | null>(null)

  const handleTextSearch = useCallback(
    async (searchText?: string) => {
      const textToSearch = searchText || queryText
      if (!textToSearch.trim()) return

      setIsSearching(true)
      try {
        const res = await SearchService.searchByText(textToSearch, topK, undefined, minScore)
        setSearchResponse(res)
      } catch (err) {
        console.error('Text search error:', err)
      } finally {
        setIsSearching(false)
      }
    },
    [queryText, topK, minScore]
  )

  const handleImageSearch = useCallback(
    async (file?: File) => {
      const fileToSearch = file || queryImage
      if (!fileToSearch) return

      setIsSearching(true)
      try {
        const res = await SearchService.searchByImage(fileToSearch, topK, undefined, minScore)
        setSearchResponse(res)
      } catch (err) {
        console.error('Image search error:', err)
      } finally {
        setIsSearching(false)
      }
    },
    [queryImage, topK, minScore]
  )

  const fetchIndexStats = useCallback(async () => {
    try {
      const stats = await SearchService.getIndexStatus()
      setIndexStats(stats)
    } catch (err) {
      console.error('Failed to fetch index stats:', err)
    }
  }, [])

  useEffect(() => {
    fetchIndexStats()
    handleTextSearch('Person wearing white shirt')
  }, [])

  const handleImageFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selected = e.target.files[0]
      setQueryImage(selected)
      const url = URL.createObjectURL(selected)
      setQueryImagePreview(url)
      handleImageSearch(selected)
    }
  }

  const handleExampleClick = (query: string) => {
    setSearchMode('text')
    setQueryText(query)
    handleTextSearch(query)
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 py-6">
      {/* Page Header & Search Mode Switcher */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight flex items-center space-x-3">
              <div className="p-2.5 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/20">
                <SearchIcon className="w-6 h-6" />
              </div>
              <span>OpenCLIP & FAISS Intelligent Video Search</span>
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Natural language text & image similarity search with interactive video timeline marker playback
            </p>
          </div>

          {/* Search Mode Toggle */}
          <div className="flex items-center bg-slate-950 p-1.5 rounded-2xl border border-slate-800 self-start sm:self-auto">
            <button
              onClick={() => setSearchMode('text')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
                searchMode === 'text'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <SearchIcon className="w-3.5 h-3.5" />
              <span>Natural Language Text</span>
            </button>
            <button
              onClick={() => setSearchMode('image')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
                searchMode === 'image'
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <ImageIcon className="w-3.5 h-3.5" />
              <span>Image Query Upload</span>
            </button>
          </div>
        </div>

        {/* Text Search Form */}
        {searchMode === 'text' ? (
          <form onSubmit={(e) => { e.preventDefault(); handleTextSearch(); }} className="relative flex items-center">
            <div className="relative flex-1">
              <SearchIcon className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                placeholder="Enter natural language query... e.g. 'Person wearing white shirt', 'Blue backpack', 'Black car', 'Red bicycle'"
                className="w-full bg-slate-950 border-2 border-slate-800 hover:border-slate-700 focus:border-indigo-500 rounded-2xl pl-12 pr-10 py-4 text-slate-100 placeholder-slate-500 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition shadow-inner text-sm"
              />
              {queryText && (
                <button
                  type="button"
                  onClick={() => setQueryText('')}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            <button
              type="submit"
              disabled={isSearching}
              className="ml-3 px-6 py-4 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-500 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm shadow-xl shadow-indigo-600/25 flex items-center space-x-2 transition shrink-0 hover:scale-[1.01]"
            >
              {isSearching ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              <span>Search FAISS</span>
            </button>
          </form>
        ) : (
          /* Image Upload Search Mode */
          <div className="bg-slate-950/80 border-2 border-dashed border-purple-500/30 hover:border-purple-500/60 rounded-2xl p-6 text-center space-y-4">
            <input
              ref={imageInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageFileChange}
              className="hidden"
            />

            {queryImagePreview ? (
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <div className="w-32 h-32 rounded-xl bg-black border border-purple-500/50 overflow-hidden shadow-lg shrink-0">
                  <img src={queryImagePreview} alt="Query" className="w-full h-full object-cover" />
                </div>

                <div className="text-left space-y-2">
                  <h4 className="text-sm font-bold text-slate-200">{queryImage?.name}</h4>
                  <p className="text-xs text-slate-400 font-mono">
                    Generating OpenCLIP 512D visual feature embedding to query FAISS index
                  </p>

                  <div className="flex items-center space-x-2 pt-1">
                    <button
                      onClick={() => handleImageSearch()}
                      disabled={isSearching}
                      className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-md transition flex items-center space-x-1.5"
                    >
                      {isSearching ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                      <span>Re-Run Search</span>
                    </button>
                    <button
                      onClick={() => {
                        setQueryImage(null)
                        setQueryImagePreview(null)
                      }}
                      className="px-3 py-2 rounded-xl bg-slate-800 text-slate-300 font-semibold text-xs hover:bg-slate-700"
                    >
                      Change Image
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div onClick={() => imageInputRef.current?.click()} className="cursor-pointer space-y-3 py-4">
                <div className="w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center mx-auto">
                  <Upload className="w-7 h-7" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-200">Upload Target Image to Find Visual Matches</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Click or drag & drop a JPEG, PNG, or WEBP image file to encode 512D OpenCLIP vector and search FAISS
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Example Pills */}
        <div className="space-y-2 pt-1">
          <span className="text-xs font-bold text-slate-300 flex items-center space-x-1.5">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span>Example Natural Language Surveillance Queries:</span>
          </span>

          <div className="flex flex-wrap gap-2">
            {NATURAL_LANGUAGE_EXAMPLES.map((item) => (
              <button
                key={item.label}
                type="button"
                onClick={() => handleExampleClick(item.query)}
                className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-950 hover:bg-slate-800 text-slate-200 border border-slate-800 transition flex items-center space-x-1.5 hover:border-indigo-500/50"
              >
                <item.icon className="w-3.5 h-3.5 text-indigo-400" />
                <span>"{item.label}"</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Controls Header & View Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-slate-900/60 border border-slate-800 rounded-2xl p-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-indigo-400" />
            <span className="text-xs font-semibold text-slate-300">Top-K Results:</span>
            {[6, 12, 24, 48].map((k) => (
              <button
                key={k}
                onClick={() => {
                  setTopK(k)
                  if (searchMode === 'text') handleTextSearch()
                  else handleImageSearch()
                }}
                className={`px-2.5 py-1 text-xs font-bold rounded-lg transition ${
                  topK === k ? 'bg-indigo-600 text-white' : 'bg-slate-950 text-slate-400 hover:text-white'
                }`}
              >
                {k}
              </button>
            ))}
          </div>

          <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setViewMode('timeline')}
              className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center space-x-1 ${
                viewMode === 'timeline' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              <span>Interactive Timeline</span>
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center space-x-1 ${
                viewMode === 'grid' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Film className="w-3.5 h-3.5" />
              <span>Match Cards Grid</span>
            </button>
          </div>
        </div>

        {searchResponse && (
          <div className="flex items-center space-x-4 text-xs font-mono text-slate-400">
            <span>Query: <strong className="text-slate-200">"{searchResponse.query_text}"</strong></span>
            <span>Matches: <strong className="text-slate-200">{searchResponse.total_matches}</strong></span>
            <span>Latency: <strong className="text-emerald-400">{searchResponse.execution_time_ms} ms</strong></span>
          </div>
        )}
      </div>

      {/* Primary Display: Interactive Video Timeline vs Match Cards Grid */}
      {isSearching ? (
        <div className="py-20 text-center space-y-4">
          <div className="w-10 h-10 border-3 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto" />
          <p className="text-sm font-medium text-slate-300">Searching FAISS index and building interactive video timeline...</p>
        </div>
      ) : !searchResponse || searchResponse.results.length === 0 ? (
        <div className="py-16 border-2 border-dashed border-slate-800 rounded-3xl text-center space-y-3">
          <Film className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-lg font-bold text-slate-200">No Match Results Found</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Try selecting one of the pre-set natural language examples above or generating OpenCLIP embeddings for uploaded videos.
          </p>
        </div>
      ) : viewMode === 'timeline' ? (
        /* Interactive Video Timeline Component */
        <InteractiveVideoTimeline
          videoTitle={searchResponse.results[0]?.video_title || 'Surveillance Video'}
          videoUrl={searchResponse.results[0]?.image_url}
          videoDuration={120}
          results={searchResponse.results}
        />
      ) : (
        /* Match Cards Grid View */
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <span>Ranked Results (Top-{searchResponse.results.length} Matches Sorted by Similarity Score)</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {searchResponse.results.map((result, idx) => (
              <div
                key={`${result.frame_id}-${result.object_id || idx}`}
                onClick={() => setSelectedResult(result)}
                className="bg-slate-900 border border-slate-800 hover:border-indigo-500/80 rounded-2xl p-4 space-y-3 cursor-pointer transition-all duration-300 hover:scale-[1.02] shadow-xl group flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="relative aspect-video bg-black rounded-xl overflow-hidden group-hover:shadow-indigo-500/10">
                    <img
                      src={result.crop_url || result.image_url}
                      alt={result.video_title}
                      className="w-full h-full object-cover"
                    />

                    <div className="absolute top-2 left-2 bg-indigo-600 text-white font-mono text-[10px] font-bold px-2 py-0.5 rounded shadow">
                      Rank #{idx + 1}
                    </div>

                    <div className="absolute top-2 right-2 bg-black/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-xs font-mono font-bold text-emerald-400 border border-emerald-500/30 flex items-center space-x-1">
                      <Zap className="w-3 h-3 text-emerald-400 fill-emerald-400" />
                      <span>{(result.similarity_score * 100).toFixed(1)}% Match</span>
                    </div>

                    <div className="absolute bottom-2 left-2 bg-black/70 backdrop-blur-md px-2 py-0.5 rounded text-[10px] font-mono text-purple-300 uppercase">
                      {result.type}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-bold text-slate-100 text-sm truncate">{result.video_title}</h4>
                    <p className="text-xs text-slate-400 flex items-center space-x-2 mt-0.5">
                      <Clock className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Timestamp: {formatDuration(result.timestamp_seconds)} (Frame #{result.frame_number})</span>
                    </p>
                  </div>
                </div>

                {result.bounding_box && (
                  <div className="border-t border-slate-800/80 pt-2 text-[11px] text-slate-400 font-mono flex items-center justify-between">
                    <span className="flex items-center space-x-1 text-purple-400 font-semibold">
                      <Crosshair className="w-3 h-3" />
                      <span>BBox [{result.bounding_box.xmin.toFixed(2)}, {result.bounding_box.ymin.toFixed(2)}]</span>
                    </span>
                    {result.label && <span className="capitalize font-bold text-slate-200">{result.label}</span>}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Result Inspector Modal Lightbox */}
      {selectedResult && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setSelectedResult(null)}
        >
          <div
            className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-4xl w-full space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                  <span>Match Detail ({(selectedResult.similarity_score * 100).toFixed(2)}% Similarity Score)</span>
                </h3>
                <p className="text-xs text-slate-400">
                  {selectedResult.video_title} — Frame #{selectedResult.frame_number} ({formatDuration(selectedResult.timestamp_seconds)})
                </p>
              </div>
              <button
                onClick={() => setSelectedResult(null)}
                className="text-xs font-semibold px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl"
              >
                Close
              </button>
            </div>

            <div className="aspect-video bg-black rounded-2xl overflow-hidden relative">
              <img
                src={selectedResult.image_url || selectedResult.crop_url}
                alt="Match"
                className="w-full h-full object-contain"
              />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono text-slate-300 bg-slate-950 p-4 rounded-2xl">
              <div>Similarity Score: <strong className="text-emerald-400">{(selectedResult.similarity_score * 100).toFixed(2)}%</strong></div>
              <div>Timestamp: <strong className="text-slate-200">{formatDuration(selectedResult.timestamp_seconds)} ({selectedResult.timestamp_seconds}s)</strong></div>
              <div>Frame Number: <strong className="text-purple-300">#{selectedResult.frame_number}</strong></div>
              <div>Bounding Box: <strong className="text-blue-300">{selectedResult.bounding_box ? `[${selectedResult.bounding_box.xmin}, ${selectedResult.bounding_box.ymin}, ${selectedResult.bounding_box.xmax}, ${selectedResult.bounding_box.ymax}]` : 'N/A'}</strong></div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
