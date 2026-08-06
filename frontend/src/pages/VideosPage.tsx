import React, { useState, useEffect, useCallback } from 'react'
import { VideoService } from '@/services/videoService'
import { Video as VideoType } from '@/types/video'
import { formatBytes, formatDuration } from '@/lib/videoValidation'
import {
  Film,
  Clock,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Search,
  Trash2,
  Scissors,
  Play,
} from 'lucide-react'
import { Link } from 'react-router-dom'

export const VideosPage: React.FC = () => {
  const [videos, setVideos] = useState<VideoType[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const fetchVideos = useCallback(async () => {
    try {
      setIsRefreshing(true)
      const data = await VideoService.getVideos(1, 50)
      setVideos(data.items || [])
    } catch (err) {
      console.error('Failed to fetch videos:', err)
    } fontally: {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }, [])

  useEffect(() => {
    fetchVideos()
  }, [fetchVideos])

  const handleDelete = async (videoId: string) => {
    if (!window.confirm('Are you sure you want to delete this video asset?')) return
    try {
      await VideoService.deleteVideo(videoId)
      fetchVideos()
    } catch (err) {
      console.error('Failed to delete video:', err)
    }
  }

  const filteredVideos = videos.filter((v) => {
    const matchesSearch = v.title.toLowerCase().includes(searchQuery.toLowerCase()) || v.id.includes(searchQuery)
    const matchesStatus = statusFilter === 'all' || v.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Ready / Indexed</span>
          </span>
        )
      case 'processing':
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            <span>Processing</span>
          </span>
        )
      case 'failed':
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Failed</span>
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Clock className="w-3.5 h-3.5" />
            <span>Pending</span>
          </span>
        )
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight flex items-center space-x-3">
            <div className="p-2 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <Film className="w-6 h-6" />
            </div>
            <span>Surveillance Video Library</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Browse ingested video assets, manage processing state, and trigger AI computer vision indexing
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchVideos}
            disabled={isRefreshing}
            className="flex items-center space-x-2 text-xs font-semibold px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh Asset Library</span>
          </button>

          <Link
            to="/upload"
            className="flex items-center space-x-2 text-xs font-bold px-4 py-2 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg transition"
          >
            <span>+ Upload Video</span>
          </Link>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col md:flex-row gap-4 justify-between bg-slate-900/60 border border-slate-800 rounded-2xl p-4">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search by video title or UUID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-400">Filter Status:</span>
          {['all', 'completed', 'processing', 'pending', 'failed'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition ${
                statusFilter === st
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Video Assets Grid/Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6">
        {isLoading ? (
          <div className="py-16 text-center text-slate-400 space-y-3">
            <div className="w-8 h-8 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mx-auto" />
            <p className="text-sm">Loading video assets...</p>
          </div>
        ) : filteredVideos.length === 0 ? (
          <div className="py-16 border-2 border-dashed border-slate-800 rounded-2xl text-center space-y-3">
            <Film className="w-12 h-12 text-slate-600 mx-auto" />
            <p className="text-slate-300 text-base font-bold">No video assets found</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Upload a surveillance video to extract keyframes, run object detection, and enable FAISS search.
            </p>
            <Link
              to="/upload"
              className="inline-block mt-2 px-4 py-2 rounded-xl text-xs font-bold bg-purple-600 text-white hover:bg-purple-500 transition"
            >
              Go to Video Upload
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVideos.map((video) => (
              <div
                key={video.id}
                className="bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition flex flex-col"
              >
                {/* Thumbnail / Video Preview */}
                <div className="relative aspect-video bg-slate-900 flex items-center justify-center border-b border-slate-800 overflow-hidden">
                  {video.playbackUrl ? (
                    <video src={video.playbackUrl} controls className="w-full h-full object-cover" />
                  ) : (
                    <div className="flex flex-col items-center justify-center space-y-2 text-slate-500">
                      <Play className="w-8 h-8 text-purple-400 opacity-60" />
                      <span className="text-xs font-mono">No Preview</span>
                    </div>
                  )}
                  <div className="absolute top-2 right-2">{getStatusBadge(video.status)}</div>
                </div>

                {/* Metadata Body */}
                <div className="p-4 flex-1 flex flex-col justify-between space-y-4">
                  <div>
                    <h4 className="font-bold text-slate-100 text-base line-clamp-1">{video.title}</h4>
                    <p className="text-xs font-mono text-slate-500 mt-0.5 truncate">{video.id}</p>
                  </div>

                  <div className="grid grid-cols-3 gap-2 py-2 px-3 bg-slate-900/80 rounded-xl text-xs border border-slate-800/80">
                    <div>
                      <span className="text-slate-500 block text-[10px]">Duration</span>
                      <span className="font-semibold text-slate-300">{formatDuration(video.durationSeconds)}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">Resolution</span>
                      <span className="font-semibold text-slate-300">
                        {video.width && video.height ? `${video.width}x${video.height}` : 'N/A'}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">File Size</span>
                      <span className="font-semibold text-slate-300">{formatBytes(video.fileSizeBytes || 0)}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between pt-2 border-t border-slate-800/60">
                    <Link
                      to="/upload"
                      className="flex items-center space-x-1 text-xs font-semibold px-3 py-1.5 rounded-lg bg-purple-600/20 text-purple-300 border border-purple-500/30 hover:bg-purple-600 hover:text-white transition"
                    >
                      <Scissors className="w-3.5 h-3.5" />
                      <span>Pipeline</span>
                    </Link>

                    <button
                      onClick={() => handleDelete(video.id)}
                      className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition"
                      title="Delete Video Asset"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
