import React, { useState, useEffect, useCallback } from 'react'
import {
  BrainCircuit,
  Play,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Search,
  Code,
} from 'lucide-react'
import { CLIPService } from '@/services/clipService'
import { CLIPEmbeddingProgress, TextEmbeddingResponse } from '@/types/embedding'

interface OpenCLIPCardProps {
  videoId: string
  videoTitle: string
}

export const OpenCLIPCard: React.FC<OpenCLIPCardProps> = ({ videoId, videoTitle: _videoTitle }) => {
  const [includeFrames, setIncludeFrames] = useState<boolean>(true)
  const [includeObjects, setIncludeObjects] = useState<boolean>(true)
  const [progress, setProgress] = useState<CLIPEmbeddingProgress | null>(null)
  const [isGenerating, setIsGenerating] = useState<boolean>(false)

  // Interactive Text Embedding Test State
  const [queryText, setQueryText] = useState<string>('red car driving at night')
  const [textEmbedding, setTextEmbedding] = useState<TextEmbeddingResponse | null>(null)
  const [isEncodingText, setIsEncodingText] = useState<boolean>(false)

  const checkStatus = useCallback(async () => {
    try {
      const status = await CLIPService.getEmbeddingStatus(videoId)
      setProgress(status)

      if (status.status === 'processing') {
        setIsGenerating(true)
      } else if (status.status === 'completed') {
        setIsGenerating(false)
      } else if (status.status === 'failed') {
        setIsGenerating(false)
      }
    } catch (err) {
      console.error('Embedding status check error:', err)
    }
  }, [videoId])

  useEffect(() => {
    checkStatus()
  }, [checkStatus])

  useEffect(() => {
    let intervalId: any
    if (isGenerating) {
      intervalId = setInterval(() => {
        checkStatus()
      }, 1500)
    }
    return () => {
      if (intervalId) clearInterval(intervalId)
    }
  }, [isGenerating, checkStatus])

  const handleStartEmbeddings = async () => {
    try {
      setIsGenerating(true)
      const res = await CLIPService.triggerEmbeddingGeneration(videoId, includeFrames, includeObjects)
      setProgress(res)
    } catch (err: any) {
      console.error('Failed to trigger OpenCLIP embedding generation:', err)
      setIsGenerating(false)
    }
  }

  const handleEncodeTextQuery = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!queryText.trim()) return
    try {
      setIsEncodingText(true)
      const res = await CLIPService.generateTextEmbedding(queryText)
      setTextEmbedding(res)
    } catch (err) {
      console.error('Failed to encode text query:', err)
    } finally {
      setIsEncodingText(false)
    }
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-pink-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-pink-500/20">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">OpenCLIP Feature Vector Embeddings</h3>
            <p className="text-xs text-slate-400">
              Generate 512D L2-normalized visual & text embeddings for pgvector similarity search
            </p>
          </div>
        </div>

        {/* Model Spec Badge */}
        <div className="flex items-center space-x-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-xs font-mono text-pink-400">
          <span className="font-bold">Model: ViT-B-32</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-300">Dim: 512</span>
        </div>
      </div>

      {/* Target Toggles */}
      <div className="flex flex-wrap items-center gap-4">
        <label className="flex items-center space-x-2 cursor-pointer bg-slate-950 px-3.5 py-2 rounded-xl border border-slate-800 text-xs font-semibold text-slate-300">
          <input
            type="checkbox"
            checked={includeFrames}
            onChange={(e) => setIncludeFrames(e.target.checked)}
            disabled={isGenerating}
            className="rounded accent-pink-500 cursor-pointer"
          />
          <span>Embed Keyframe Images</span>
        </label>

        <label className="flex items-center space-x-2 cursor-pointer bg-slate-950 px-3.5 py-2 rounded-xl border border-slate-800 text-xs font-semibold text-slate-300">
          <input
            type="checkbox"
            checked={includeObjects}
            onChange={(e) => setIncludeObjects(e.target.checked)}
            disabled={isGenerating}
            className="rounded accent-pink-500 cursor-pointer"
          />
          <span>Embed Cropped Detected Objects</span>
        </label>
      </div>

      {/* Trigger Button or Progress Bar */}
      {!isGenerating && (!progress || progress.status === 'pending' || progress.status === 'failed') ? (
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-5 h-5 text-pink-400 shrink-0" />
            <p className="text-xs text-slate-300">
              Batch encode keyframes & object crops into 512D normalized feature vectors and save to PostgreSQL <code className="text-pink-300 font-mono">embeddings</code> table.
            </p>
          </div>

          <button
            onClick={handleStartEmbeddings}
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-pink-600 hover:bg-pink-500 text-white font-bold text-xs shadow-lg shadow-pink-600/25 flex items-center justify-center space-x-2 transition shrink-0"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Generate 512D Embeddings</span>
          </button>
        </div>
      ) : (
        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {progress?.status === 'completed' ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              ) : progress?.status === 'failed' ? (
                <AlertTriangle className="w-5 h-5 text-red-400" />
              ) : (
                <RefreshCw className="w-5 h-5 text-pink-400 animate-spin" />
              )}
              <div>
                <h4 className="text-sm font-bold text-slate-200">
                  {progress?.status === 'completed'
                    ? `Embeddings Completed (${progress.frame_embeddings_count} Keyframe Vectors, ${progress.object_embeddings_count} Object Vectors)`
                    : progress?.status === 'failed'
                    ? 'Embedding Generation Failed'
                    : 'Batch Encoding OpenCLIP Feature Vectors...'}
                </h4>
                <p className="text-xs text-slate-400">
                  Processed {progress?.processed_items || 0} / {progress?.total_items || 0} items (
                  {progress?.progress_percent || 0}%)
                </p>
              </div>
            </div>
          </div>

          <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${
                progress?.status === 'completed'
                  ? 'bg-emerald-500'
                  : progress?.status === 'failed'
                  ? 'bg-red-500'
                  : 'bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-400 animate-pulse'
              }`}
              style={{ width: `${progress?.progress_percent || 0}%` }}
            />
          </div>

          {progress?.error_message && (
            <p className="text-xs text-red-400 font-medium">{progress.error_message}</p>
          )}
        </div>
      )}

      {/* Interactive Natural Language Text Vector Tester */}
      <div className="bg-slate-950 border border-slate-800/80 rounded-2xl p-5 space-y-4">
        <div className="flex items-center space-x-2 text-xs font-bold text-slate-200">
          <Search className="w-4 h-4 text-pink-400" />
          <span>Test OpenCLIP Text Query Vector Encoding</span>
        </div>

        <form onSubmit={handleEncodeTextQuery} className="flex gap-2">
          <input
            type="text"
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            placeholder="Enter natural language query (e.g. red car in parking lot)"
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-pink-500"
          />
          <button
            type="submit"
            disabled={isEncodingText}
            className="px-4 py-2 rounded-xl bg-pink-600 hover:bg-pink-500 text-white font-bold text-xs shadow-md transition flex items-center space-x-1"
          >
            {isEncodingText ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Code className="w-3.5 h-3.5" />}
            <span>Encode Vector</span>
          </button>
        </form>

        {textEmbedding && (
          <div className="space-y-2 pt-2 border-t border-slate-900">
            <div className="flex justify-between items-center text-[11px] text-slate-400 font-mono">
              <span>Text: <strong className="text-slate-200">"{textEmbedding.query_text}"</strong></span>
              <span>Model: <strong className="text-pink-400">{textEmbedding.model_name}</strong> ({textEmbedding.dimension}D)</span>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 max-h-24 overflow-y-auto">
              <p className="text-[10px] font-mono text-pink-300/90 leading-relaxed break-all">
                [{textEmbedding.embedding.slice(0, 30).join(', ')}, ... {textEmbedding.embedding.length - 30} more values]
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
