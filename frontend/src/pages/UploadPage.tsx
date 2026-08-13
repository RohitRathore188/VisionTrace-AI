import React, { useState, useEffect, useCallback } from 'react'
import { VideoUploadCard } from '@/components/upload/VideoUploadCard'
import { FrameExtractionCard } from '@/components/upload/FrameExtractionCard'
import { YOLODetectionCard } from '@/components/upload/YOLODetectionCard'
import { ByteTrackCard } from '@/components/upload/ByteTrackCard'
import { OpenCLIPCard } from '@/components/upload/OpenCLIPCard'
import { FAISSIndexCard } from '@/components/upload/FAISSIndexCard'
import { VideoService } from '@/services/videoService'
import { Video } from '@/types/video'
import { formatBytes, formatDuration } from '@/lib/videoValidation'
import {
  Film,
  Clock,
  CheckCircle2,
  AlertCircle,
  Trash2,
  RefreshCw,
  Layers,
  Scissors,
  Scan,
  Route,
  BrainCircuit,
  Database,
  X,
  Play,
} from 'lucide-react'

export const UploadPage: React.FC = () => {
  const [videos, setVideos] = useState<Video[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [selectedVideoForProcessing, setSelectedVideoForProcessing] = useState<Video | null>(null)
  const [activeTab, setActiveTab] = useState<'extraction' | 'detection' | 'tracking' | 'embeddings' | 'faiss'>('extraction')
  const [previewingVideo, setPreviewingVideo] = useState<Video | null>(null)

  const fetchVideos = useCallback(async (autoSelectVideo?: Video) => {
    try {
      setIsRefreshing(true)
      const data = await VideoService.getVideos(1, 20)
      setVideos(data.items || [])
      if (autoSelectVideo) {
        setSelectedVideoForProcessing(autoSelectVideo)
      } else if (data.items && data.items.length > 0 && !selectedVideoForProcessing) {
        setSelectedVideoForProcessing(data.items[0])
      }
    } catch (err) {
      console.error('Failed to fetch videos:', err)
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }, [selectedVideoForProcessing])

  useEffect(() => {
    fetchVideos()
  }, [fetchVideos])

  const handleUploadSuccess = async (newVideo?: Video) => {
    await fetchVideos(newVideo)
    if (newVideo) {
      setSelectedVideoForProcessing(newVideo)
      setActiveTab('extraction')
    }
  }

  // Live Status Auto Polling when videos are processing
  useEffect(() => {
    const hasProcessing = videos.some((v) => v.status === 'processing')
    let timer: any = null
    if (hasProcessing) {
      timer = setInterval(() => {
        fetchVideos()
      }, 2500)
    }
    return () => {
      if (timer) clearInterval(timer)
    }
  }, [videos, fetchVideos])

  const handleDelete = async (videoId: string) => {
    if (!window.confirm('Are you sure you want to delete this video asset?')) return
    try {
      await VideoService.deleteVideo(videoId)
      if (selectedVideoForProcessing?.id === videoId) {
        setSelectedVideoForProcessing(null)
      }
      fetchVideos()
    } catch (err) {
      console.error('Failed to delete video:', err)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Ready / Completed</span>
          </span>
        )
      case 'processing':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 shadow">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            <span>Processing Pipeline</span>
          </span>
        )
      case 'failed':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20 shadow">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Failed</span>
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow">
            <Clock className="w-3.5 h-3.5" />
            <span>Pending</span>
          </span>
        )
    }
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 py-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight flex items-center space-x-3">
            <div className="p-2 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Film className="w-6 h-6" />
            </div>
            <span>Surveillance Pipeline & AI Vision Indexing</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Ingest video footage, extract keyframes, run YOLO detection, track motion via ByteTrack, and generate OpenCLIP 512D embeddings
          </p>
        </div>

        <button
          onClick={() => fetchVideos()}
          disabled={isRefreshing}
          className="flex items-center space-x-2 text-xs font-semibold px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Main Video Upload Card */}
      <VideoUploadCard onUploadSuccess={handleUploadSuccess} />

      {/* Selected Video Pipeline Tabs */}
      {selectedVideoForProcessing && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-2 overflow-x-auto">
            <button
              onClick={() => setActiveTab('extraction')}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl font-bold text-xs transition ${
                activeTab === 'extraction'
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              <Scissors className="w-4 h-4" />
              <span>1. Keyframes</span>
            </button>

            <button
              onClick={() => setActiveTab('detection')}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl font-bold text-xs transition ${
                activeTab === 'detection'
                  ? 'bg-emerald-600 text-white shadow-md'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              <Scan className="w-4 h-4" />
              <span>2. YOLO Objects</span>
            </button>

            <button
              onClick={() => setActiveTab('tracking')}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl font-bold text-xs transition ${
                activeTab === 'tracking'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              <Route className="w-4 h-4" />
              <span>3. ByteTrack</span>
            </button>

            <button
              onClick={() => setActiveTab('embeddings')}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl font-bold text-xs transition ${
                activeTab === 'embeddings'
                  ? 'bg-pink-600 text-white shadow-md'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              <BrainCircuit className="w-4 h-4" />
              <span>4. OpenCLIP 512D</span>
            </button>

            <button
              onClick={() => setActiveTab('faiss')}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl font-bold text-xs transition ${
                activeTab === 'faiss'
                  ? 'bg-cyan-600 text-white shadow-md'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              <Database className="w-4 h-4" />
              <span>5. FAISS Index</span>
            </button>

            <span className="text-xs text-slate-500 font-mono hidden lg:inline ml-auto">
              Active Video: <strong className="text-slate-300">{selectedVideoForProcessing.title}</strong>
            </span>
          </div>

          {activeTab === 'extraction' ? (
            <FrameExtractionCard
              key={`extract-${selectedVideoForProcessing.id}`}
              videoId={selectedVideoForProcessing.id}
              videoTitle={selectedVideoForProcessing.title}
              onCompleted={fetchVideos}
            />
          ) : activeTab === 'detection' ? (
            <YOLODetectionCard
              key={`detect-${selectedVideoForProcessing.id}`}
              videoId={selectedVideoForProcessing.id}
              videoTitle={selectedVideoForProcessing.title}
            />
          ) : activeTab === 'tracking' ? (
            <ByteTrackCard
              key={`track-${selectedVideoForProcessing.id}`}
              videoId={selectedVideoForProcessing.id}
              videoTitle={selectedVideoForProcessing.title}
            />
          ) : activeTab === 'embeddings' ? (
            <OpenCLIPCard
              key={`clip-${selectedVideoForProcessing.id}`}
              videoId={selectedVideoForProcessing.id}
              videoTitle={selectedVideoForProcessing.title}
            />
          ) : (
            <FAISSIndexCard />
          )}
        </div>
      )}

      {/* Ingested Video Queue Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Layers className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-bold text-slate-100">Ingested Video Assets ({videos.length})</h3>
          </div>
        </div>

        {isLoading ? (
          <div className="py-12 text-center text-slate-400 space-y-3">
            <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto" />
            <p className="text-sm">Loading ingested video assets...</p>
          </div>
        ) : videos.length === 0 ? (
          <div className="py-12 border-2 border-dashed border-slate-800 rounded-2xl text-center space-y-3">
            <Film className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-slate-400 text-sm font-medium">No video assets ingested yet</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Use the uploader above to ingest MP4, AVI, MOV, or MKV surveillance files.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-4">Video Asset</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Duration</th>
                  <th className="py-3 px-4">Resolution</th>
                  <th className="py-3 px-4">File Size</th>
                  <th className="py-3 px-4 text-right">Pipeline Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-sm">
                {videos.map((video) => {
                  const thumbImg = video.thumbnailUrl || (video.metadataJson && video.metadataJson.thumbnail_url)
                  return (
                    <tr
                      key={video.id}
                      className={`hover:bg-slate-800/30 transition group ${
                        selectedVideoForProcessing?.id === video.id ? 'bg-purple-500/5' : ''
                      }`}
                    >
                      <td className="py-3.5 px-4">
                        <div className="flex items-center space-x-3">
                          <div
                            onClick={() => setPreviewingVideo(video)}
                            className="w-12 h-10 rounded-lg bg-slate-950 border border-slate-800 hover:border-purple-500 flex items-center justify-center text-indigo-400 font-bold shrink-0 overflow-hidden cursor-pointer group/thumb relative"
                          >
                            {thumbImg ? (
                              <img src={thumbImg} alt={video.title} className="w-full h-full object-cover" />
                            ) : video.playbackUrl ? (
                              <video src={video.playbackUrl} className="w-full h-full object-cover" />
                            ) : (
                              <Film className="w-5 h-5" />
                            )}
                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover/thumb:opacity-100 flex items-center justify-center transition">
                              <Play className="w-4 h-4 text-white fill-white" />
                            </div>
                          </div>
                          <div className="min-w-0">
                            <p className="font-semibold text-slate-200 truncate max-w-xs">{video.title}</p>
                            <p className="text-xs text-slate-500 font-mono truncate">{video.id}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">{getStatusBadge(video.status)}</td>
                      <td className="py-3.5 px-4 text-slate-300 font-medium">
                        {formatDuration(video.durationSeconds)}
                      </td>
                      <td className="py-3.5 px-4 text-slate-400">
                        {video.width && video.height ? `${video.width}x${video.height}` : 'N/A'}
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 font-mono text-xs">
                        {formatBytes(video.fileSizeBytes || 0)}
                      </td>
                      <td className="py-3.5 px-4 text-right flex items-center justify-end space-x-1 sm:space-x-2">
                        <button
                          onClick={() => {
                            setSelectedVideoForProcessing(video)
                            setActiveTab('extraction')
                          }}
                          className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                            selectedVideoForProcessing?.id === video.id && activeTab === 'extraction'
                              ? 'bg-purple-600 text-white'
                              : 'bg-slate-800 text-slate-300 hover:bg-purple-600 hover:text-white'
                          }`}
                        >
                          <Scissors className="w-3.5 h-3.5" />
                          <span className="hidden sm:inline">Keyframes</span>
                        </button>

                        <button
                          onClick={() => {
                            setSelectedVideoForProcessing(video)
                            setActiveTab('detection')
                          }}
                          className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                            selectedVideoForProcessing?.id === video.id && activeTab === 'detection'
                              ? 'bg-emerald-600 text-white'
                              : 'bg-slate-800 text-slate-300 hover:bg-emerald-600 hover:text-white'
                          }`}
                        >
                          <Scan className="w-3.5 h-3.5" />
                          <span className="hidden sm:inline">YOLO</span>
                        </button>

                        <button
                          onClick={() => {
                            setSelectedVideoForProcessing(video)
                            setActiveTab('tracking')
                          }}
                          className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                            selectedVideoForProcessing?.id === video.id && activeTab === 'tracking'
                              ? 'bg-blue-600 text-white'
                              : 'bg-slate-800 text-slate-300 hover:bg-blue-600 hover:text-white'
                          }`}
                        >
                          <Route className="w-3.5 h-3.5" />
                          <span className="hidden sm:inline">ByteTrack</span>
                        </button>

                        <button
                          onClick={() => {
                            setSelectedVideoForProcessing(video)
                            setActiveTab('embeddings')
                          }}
                          className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                            selectedVideoForProcessing?.id === video.id && activeTab === 'embeddings'
                              ? 'bg-pink-600 text-white'
                              : 'bg-slate-800 text-slate-300 hover:bg-pink-600 hover:text-white'
                          }`}
                        >
                          <BrainCircuit className="w-3.5 h-3.5" />
                          <span className="hidden sm:inline">CLIP</span>
                        </button>

                        <button
                          onClick={() => handleDelete(video.id)}
                          className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition"
                          title="Delete Video"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Video Player Preview Modal */}
      {previewingVideo && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setPreviewingVideo(null)}
        >
          <div
            className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-4xl w-full space-y-4 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  <Film className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-100 text-lg">{previewingVideo.title}</h3>
                  <p className="text-xs text-slate-500 font-mono">{previewingVideo.id}</p>
                </div>
              </div>

              <button
                onClick={() => setPreviewingVideo(null)}
                className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="aspect-video bg-black rounded-2xl overflow-hidden border border-slate-800 shadow-inner">
              {previewingVideo.playbackUrl ? (
                <video src={previewingVideo.playbackUrl} controls autoPlay className="w-full h-full object-contain" />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 space-y-2">
                  <Film className="w-10 h-10 text-slate-600" />
                  <p className="text-sm">Video file playback URL not available</p>
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950 p-4 rounded-2xl border border-slate-800/80 text-xs">
              <div>
                <span className="text-slate-500 block text-[10px]">Duration</span>
                <span className="font-bold text-slate-200">{formatDuration(previewingVideo.durationSeconds)}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">Resolution</span>
                <span className="font-bold text-slate-200">
                  {previewingVideo.width && previewingVideo.height ? `${previewingVideo.width}x${previewingVideo.height}` : 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">FPS / Total Frames</span>
                <span className="font-bold text-slate-200">
                  {previewingVideo.fps ? `${roundTwo(previewingVideo.fps)} FPS (${previewingVideo.totalFrames || 0} frames)` : 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">File Size</span>
                <span className="font-bold text-slate-200">{formatBytes(previewingVideo.fileSizeBytes || 0)}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function roundTwo(val: number): number {
  return Math.round(val * 100) / 100
}

