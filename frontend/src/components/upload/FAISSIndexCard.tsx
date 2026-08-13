import React, { useState, useEffect, useCallback } from 'react'
import { Database, RefreshCw, CheckCircle2, Server, Cpu, HardDrive, ShieldCheck } from 'lucide-react'
import { api } from '@/lib/api'

interface FAISSIndexStatus {
  total_vectors: number
  dimension: number
  index_type: string
  is_faiss_native: boolean
  index_file: string
}

export const FAISSIndexCard: React.FC = () => {
  const [status, setStatus] = useState<FAISSIndexStatus | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const fetchIndexStatus = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const res = await api.get<FAISSIndexStatus>('/search/index-status')
      setStatus(res.data)
    } catch (err: any) {
      console.error('Failed to fetch FAISS index status:', err)
      setError(err?.response?.data?.error?.message || 'Failed to connect to FAISS index service')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchIndexStatus()
  }, [fetchIndexStatus])

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">FAISS Vector Index Engine</h3>
            <p className="text-xs text-slate-400">
              High-speed similarity search vector database status and index sync statistics
            </p>
          </div>
        </div>

        <button
          onClick={fetchIndexStatus}
          disabled={isLoading}
          className="flex items-center space-x-2 text-xs font-semibold px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Status</span>
        </button>
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-slate-400 space-y-3">
          <div className="w-8 h-8 border-2 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mx-auto" />
          <p className="text-sm">Inspecting FAISS vector index database...</p>
        </div>
      ) : error ? (
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-xs font-mono text-red-300">
          <strong>FAISS Error:</strong> {error}
        </div>
      ) : status ? (
        <div className="space-y-6">
          {/* Status Metrics Banner */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-950 border border-slate-800/80 rounded-2xl p-4 space-y-1">
              <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
                <span>Vector Count</span>
                <Database className="w-4 h-4 text-cyan-400" />
              </div>
              <p className="text-2xl font-extrabold text-slate-100">{status.total_vectors.toLocaleString()}</p>
              <p className="text-[10px] text-slate-500">Indexed OpenCLIP Embeddings</p>
            </div>

            <div className="bg-slate-950 border border-slate-800/80 rounded-2xl p-4 space-y-1">
              <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
                <span>Vector Dimensions</span>
                <Cpu className="w-4 h-4 text-purple-400" />
              </div>
              <p className="text-2xl font-extrabold text-slate-100">{status.dimension}D</p>
              <p className="text-[10px] text-slate-500">ViT-B-32 Feature Vectors</p>
            </div>

            <div className="bg-slate-950 border border-slate-800/80 rounded-2xl p-4 space-y-1">
              <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
                <span>Index Engine</span>
                <Server className="w-4 h-4 text-emerald-400" />
              </div>
              <p className="text-xl font-bold text-slate-100 truncate">{status.index_type}</p>
              <p className="text-[10px] text-slate-500">
                {status.is_faiss_native ? 'Native C++ FAISS GPU/CPU' : 'High-Speed NumPy Engine'}
              </p>
            </div>

            <div className="bg-slate-950 border border-slate-800/80 rounded-2xl p-4 space-y-1">
              <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
                <span>Search Readiness</span>
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="pt-1">
                <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Ready for Query</span>
                </span>
              </div>
            </div>
          </div>

          {/* Index File Storage Path */}
          <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs">
            <div className="flex items-center space-x-2.5 min-w-0">
              <HardDrive className="w-4 h-4 text-cyan-400 shrink-0" />
              <div className="min-w-0">
                <span className="text-slate-400 block text-[10px]">Index File Location</span>
                <code className="text-slate-300 font-mono truncate block">{status.index_file}</code>
              </div>
            </div>

            <span className="px-2.5 py-1 rounded-lg bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-bold text-[11px] shrink-0 self-start sm:self-auto">
              Auto-Synchronized
            </span>
          </div>
        </div>
      ) : null}
    </div>
  )
}
