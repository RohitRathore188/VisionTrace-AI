import React, { useState, useRef, useEffect } from 'react'
import { SearchResultItem } from '@/types/search'
import { formatDuration } from '@/lib/videoValidation'
import {
  Play,
  Pause,
  Zap,
  Film,
  Volume2,
  VolumeX,
} from 'lucide-react'

interface InteractiveVideoTimelineProps {
  videoTitle: string
  videoUrl?: string
  videoDuration?: number // total video duration in seconds
  results: SearchResultItem[]
}

export const InteractiveVideoTimeline: React.FC<InteractiveVideoTimelineProps> = ({
  videoTitle,
  videoUrl,
  videoDuration = 120, // default fallback 2 minutes if duration unparsed
  results,
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const [isPlaying, setIsPlaying] = useState<boolean>(false)
  const [currentTime, setCurrentTime] = useState<number>(0)
  const [activeMatch, setActiveMatch] = useState<SearchResultItem | null>(
    results.length > 0 ? results[0] : null
  )
  const [hoveredMatch, setHoveredMatch] = useState<SearchResultItem | null>(null)
  const [playbackRate, setPlaybackRate] = useState<number>(1.0)
  const [isMuted, setIsMuted] = useState<boolean>(false)

  // Calculate maximum duration from video prop or highest result timestamp
  const maxTimestamp = Math.max(
    videoDuration,
    ...results.map((r) => r.timestamp_seconds + 5)
  )

  useEffect(() => {
    if (results.length > 0 && !activeMatch) {
      setActiveMatch(results[0])
    }
  }, [results, activeMatch])

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
    }
  }

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const jumpToTimestamp = (match: SearchResultItem) => {
    setActiveMatch(match)
    if (videoRef.current) {
      videoRef.current.currentTime = match.timestamp_seconds
      videoRef.current.play().catch(() => {})
      setIsPlaying(true)
    }
  }

  const handleSeekTrackClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const clickX = e.clientX - rect.left
    const percent = Math.max(0, Math.min(1, clickX / rect.width))
    const seekTime = percent * maxTimestamp

    if (videoRef.current) {
      videoRef.current.currentTime = seekTime
      setCurrentTime(seekTime)
    }
  }

  const changePlaybackSpeed = (rate: number) => {
    setPlaybackRate(rate)
    if (videoRef.current) {
      videoRef.current.playbackRate = rate
    }
  }

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted
      setIsMuted(!isMuted)
    }
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
      {/* Timeline Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center font-bold">
            <Film className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">{videoTitle} — Interactive Match Timeline</h3>
            <p className="text-xs text-slate-400">
              Click any similarity match marker on the video scrubber to jump to exact timestamp with smooth playback
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs text-slate-400 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
          <span>Match Count: <strong className="text-emerald-400">{results.length}</strong></span>
        </div>
      </div>

      {/* Video Player Box */}
      <div className="relative aspect-video bg-black rounded-2xl overflow-hidden border border-slate-800 shadow-2xl group">
        {videoUrl ? (
          <video
            ref={videoRef}
            src={videoUrl}
            onTimeUpdate={handleTimeUpdate}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center space-y-3 bg-slate-950">
            {activeMatch?.image_url || activeMatch?.crop_url ? (
              <img
                src={activeMatch.crop_url || activeMatch.image_url}
                alt="Match Preview"
                className="w-full h-full object-contain opacity-90"
              />
            ) : (
              <Film className="w-12 h-12 text-slate-600 animate-pulse" />
            )}
          </div>
        )}

        {/* Bounding Box Visual Overlay on Active Match */}
        {activeMatch && activeMatch.bounding_box && (
          <div
            className="absolute border-2 border-emerald-400 bg-emerald-500/10 rounded-lg pointer-events-none transition-all duration-300 shadow-[0_0_15px_rgba(52,211,153,0.5)]"
            style={{
              left: `${activeMatch.bounding_box.xmin * 100}%`,
              top: `${activeMatch.bounding_box.ymin * 100}%`,
              width: `${(activeMatch.bounding_box.xmax - activeMatch.bounding_box.xmin) * 100}%`,
              height: `${(activeMatch.bounding_box.ymax - activeMatch.bounding_box.ymin) * 100}%`,
            }}
          >
            <span className="absolute -top-5 left-0 bg-emerald-500 text-black font-bold font-mono text-[10px] px-1.5 py-0.5 rounded shadow uppercase">
              {activeMatch.label || 'Matched Object'} ({(activeMatch.similarity_score * 100).toFixed(1)}%)
            </span>
          </div>
        )}

        {/* Player Controls Bar Overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/60 to-transparent p-4 flex items-center justify-between text-white opacity-95 transition-opacity">
          <div className="flex items-center space-x-3">
            <button
              onClick={togglePlay}
              className="w-10 h-10 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center transition shadow-lg"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
            </button>

            <button onClick={toggleMute} className="text-slate-300 hover:text-white p-2">
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>

            <span className="font-mono text-xs text-slate-300">
              {formatDuration(currentTime)} / {formatDuration(maxTimestamp)}
            </span>
          </div>

          {/* Speed Selectors */}
          <div className="flex items-center space-x-1 font-mono text-xs bg-slate-950/80 px-2 py-1 rounded-xl border border-slate-800">
            {[0.5, 1.0, 1.5, 2.0].map((rate) => (
              <button
                key={rate}
                onClick={() => changePlaybackSpeed(rate)}
                className={`px-2 py-0.5 rounded transition ${
                  playbackRate === rate ? 'bg-indigo-600 text-white font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                {rate}x
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Interactive Match Timeline Scrubber Bar */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
          <span className="flex items-center space-x-1.5">
            <Zap className="w-4 h-4 text-emerald-400" />
            <span>Interactive Match Timeline Track (Click pin to jump to timestamp)</span>
          </span>
          <span className="font-mono text-slate-400">Total Duration: {formatDuration(maxTimestamp)}</span>
        </div>

        {/* Timeline Scrubber Track */}
        <div
          onClick={handleSeekTrackClick}
          className="relative w-full h-8 bg-slate-950 border border-slate-800 rounded-2xl cursor-pointer overflow-visible group"
        >
          {/* Current Video Playback Head Indicator */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-indigo-400 z-20 shadow-[0_0_10px_#818cf8]"
            style={{ left: `${(currentTime / maxTimestamp) * 100}%` }}
          >
            <div className="w-3 h-3 rounded-full bg-indigo-500 border-2 border-white -ml-1.25 -mt-1 shadow" />
          </div>

          {/* Render Similarity Match Markers on Scrubber Track */}
          {results.map((match, idx) => {
            const posPercent = (match.timestamp_seconds / maxTimestamp) * 100
            const isSelected = activeMatch?.frame_id === match.frame_id
            const isHovered = hoveredMatch?.frame_id === match.frame_id

            return (
              <div
                key={`${match.frame_id}-${idx}`}
                onClick={(e) => {
                  e.stopPropagation()
                  jumpToTimestamp(match)
                }}
                onMouseEnter={() => setHoveredMatch(match)}
                onMouseLeave={() => setHoveredMatch(null)}
                className="absolute top-1/2 -translate-y-1/2 z-10 cursor-pointer transition-transform hover:scale-125"
                style={{ left: `${posPercent}%` }}
              >
                {/* Marker Pin */}
                <div
                  className={`w-3.5 h-6 rounded-md border flex items-center justify-center shadow-lg transition-all ${
                    isSelected
                      ? 'bg-pink-500 border-white shadow-pink-500/50 scale-125 z-30'
                      : match.similarity_score > 0.85
                      ? 'bg-emerald-500 border-emerald-300 shadow-emerald-500/40'
                      : 'bg-indigo-500 border-indigo-300 shadow-indigo-500/30'
                  }`}
                />

                {/* Marker Tooltip Preview on Hover */}
                {(isHovered || isSelected) && (
                  <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-40 bg-slate-900 border border-slate-700 rounded-xl p-2.5 shadow-2xl w-44 space-y-1.5 pointer-events-none">
                    {match.crop_url || match.image_url ? (
                      <div className="w-full aspect-video rounded-lg bg-black overflow-hidden border border-slate-800">
                        <img src={match.crop_url || match.image_url} alt="Preview" className="w-full h-full object-cover" />
                      </div>
                    ) : null}

                    <div className="flex justify-between items-center text-[10px] font-mono">
                      <span className="text-slate-300">{formatDuration(match.timestamp_seconds)}</span>
                      <strong className="text-emerald-400 font-bold">{(match.similarity_score * 100).toFixed(1)}% Match</strong>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Horizontal Carousel of All Similarity Match Cards */}
      <div className="space-y-3 pt-2">
        <h4 className="text-xs font-bold text-slate-300 flex items-center justify-between">
          <span>Similarity Match Timeline Cards ({results.length})</span>
          <span className="text-[11px] text-slate-500 font-mono">Click card to jump video playback</span>
        </h4>

        <div className="flex space-x-3 overflow-x-auto pb-3 pt-1 scrollbar-thin scrollbar-thumb-slate-800">
          {results.map((match, idx) => {
            const isSelected = activeMatch?.frame_id === match.frame_id
            return (
              <div
                key={`${match.frame_id}-card-${idx}`}
                onClick={() => jumpToTimestamp(match)}
                className={`w-52 shrink-0 bg-slate-950 border rounded-2xl p-3 space-y-2 cursor-pointer transition-all hover:scale-[1.02] ${
                  isSelected ? 'border-pink-500 bg-pink-500/5 ring-1 ring-pink-500' : 'border-slate-800 hover:border-indigo-500/60'
                }`}
              >
                <div className="relative aspect-video rounded-xl bg-black overflow-hidden">
                  <img src={match.crop_url || match.image_url} alt="Match" className="w-full h-full object-cover" />
                  <div className="absolute top-1.5 right-1.5 bg-black/80 backdrop-blur px-2 py-0.5 rounded text-[10px] font-mono font-bold text-emerald-400">
                    {(match.similarity_score * 100).toFixed(1)}%
                  </div>
                </div>

                <div className="flex justify-between items-center text-[11px] font-mono border-t border-slate-900 pt-1.5">
                  <span className="text-slate-200 font-bold">{formatDuration(match.timestamp_seconds)}</span>
                  <span className="text-slate-500">Frame #{match.frame_number}</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
