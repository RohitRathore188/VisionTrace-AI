import React, { useState, useRef, useEffect, useCallback } from 'react'
import { SearchResultItem } from '@/types/search'
import { formatDuration } from '@/lib/videoValidation'
import { ByteTrackService, TrackData } from '@/services/bytetrackService'
import {
  Play,
  Pause,
  Zap,
  Film,
  Volume2,
  VolumeX,
  Maximize,
  Eye,
  Crosshair,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react'

interface InteractiveVideoTimelineProps {
  videoTitle: string
  videoUrl?: string
  videoId?: string
  videoDuration?: number
  results: SearchResultItem[]
  selectedMatch?: SearchResultItem | null
  onMatchSelect?: (match: SearchResultItem) => void
}

interface BBoxPixelCoords {
  left: number
  top: number
  width: number
  height: number
}

export const InteractiveVideoTimeline: React.FC<InteractiveVideoTimelineProps> = ({
  videoTitle,
  videoUrl,
  videoId,
  videoDuration = 120,
  results,
  selectedMatch,
  onMatchSelect,
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const animationFrameRef = useRef<number | null>(null)

  const [isPlaying, setIsPlaying] = useState<boolean>(false)
  const [currentTime, setCurrentTime] = useState<number>(0)
  const [activeMatch, setActiveMatch] = useState<SearchResultItem | null>(
    selectedMatch || (results.length > 0 ? results[0] : null)
  )
  const [hoveredMatch, setHoveredMatch] = useState<SearchResultItem | null>(null)
  const [playbackRate, setPlaybackRate] = useState<number>(1.0)
  const [isMuted, setIsMuted] = useState<boolean>(false)

  // Track Overlay States
  const [allTracks, setAllTracks] = useState<TrackData[]>([])
  const [showAllTracks, setShowAllTracks] = useState<boolean>(false)
  const [targetTrack, setTargetTrack] = useState<TrackData | null>(null)
  const [targetBoxCoords, setTargetBoxCoords] = useState<BBoxPixelCoords | null>(null)
  const [trackStatus, setTrackStatus] = useState<'TRACKING' | 'LOST' | 'ENDED' | 'AWAITING'>('AWAITING')

  // Load all tracks for the current video
  const activeVideoId = activeMatch?.video_id || videoId

  useEffect(() => {
    if (!activeVideoId) return
    let isMounted = true

    ByteTrackService.getAllTrajectories(activeVideoId)
      .then((data) => {
        if (isMounted) {
          setAllTracks(data.tracks || [])
        }
      })
      .catch((err) => {
        console.error('Failed to load ByteTrack trajectories:', err)
      })

    return () => {
      isMounted = false
    }
  }, [activeVideoId])

  // Sync activeMatch & seek when selectedMatch prop changes
  useEffect(() => {
    if (selectedMatch) {
      setActiveMatch(selectedMatch)
      if (videoRef.current) {
        videoRef.current.currentTime = selectedMatch.timestamp_seconds
        videoRef.current.play().catch(() => {})
        setIsPlaying(true)
      }
    }
  }, [selectedMatch])

  // Locate active target track object whenever activeMatch or allTracks change
  useEffect(() => {
    if (!activeMatch) return

    let matchedTrack: TrackData | null = null
    if (activeMatch.track_id) {
      matchedTrack = allTracks.find((t) => t.track_id === activeMatch.track_id) || null
    }

    // Fallback: if track_id is not directly attached, find track matching object_id or label near timestamp
    if (!matchedTrack && allTracks.length > 0) {
      matchedTrack =
        allTracks.find(
          (t) =>
            t.label === activeMatch.label &&
            activeMatch.timestamp_seconds >= t.first_seen - 2.0 &&
            activeMatch.timestamp_seconds <= t.last_seen + 2.0
        ) || allTracks[0]
    }

    setTargetTrack(matchedTrack)
  }, [activeMatch, allTracks])

  // Maximum timeline duration calculation
  const maxTimestamp = Math.max(
    videoDuration,
    ...results.map((r) => r.timestamp_seconds + 5)
  )

  const togglePlay = useCallback(() => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }, [isPlaying])

  const toggleMute = useCallback(() => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted
      setIsMuted(!isMuted)
    }
  }, [isMuted])

  const toggleFullscreen = useCallback(() => {
    if (containerRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {})
      } else {
        containerRef.current.requestFullscreen().catch(() => {})
      }
    }
  }, [])

  // Calculate scaled pixel coordinates for object-fit: contain letterboxing
  const calculateScaledCoords = (
    bbox: { xmin: number; ymin: number; xmax: number; ymax: number },
    videoEl: HTMLVideoElement,
    containerEl: HTMLDivElement
  ): BBoxPixelCoords => {
    const videoWidth = videoEl.videoWidth || 1920
    const videoHeight = videoEl.videoHeight || 1080
    const containerWidth = containerEl.clientWidth
    const containerHeight = containerEl.clientHeight

    const videoAspect = videoWidth / videoHeight
    const containerAspect = containerWidth / containerHeight

    let renderWidth = containerWidth
    let renderHeight = containerHeight
    let offsetX = 0
    let offsetY = 0

    if (containerAspect > videoAspect) {
      renderHeight = containerHeight
      renderWidth = renderHeight * videoAspect
      offsetX = (containerWidth - renderWidth) / 2
    } else {
      renderWidth = containerWidth
      renderHeight = renderWidth / videoAspect
      offsetY = (containerHeight - renderHeight) / 2
    }

    return {
      left: offsetX + bbox.xmin * renderWidth,
      top: offsetY + bbox.ymin * renderHeight,
      width: (bbox.xmax - bbox.xmin) * renderWidth,
      height: (bbox.ymax - bbox.ymin) * renderHeight,
    }
  }

  // Linear Interpolation helper between 2 keyframe timestamps
  const interpolateBBox = (
    p1: { timestamp_seconds: number; bounding_box: any },
    p2: { timestamp_seconds: number; bounding_box: any },
    t: number
  ) => {
    const tSpan = p2.timestamp_seconds - p1.timestamp_seconds
    if (tSpan <= 0) return p1.bounding_box

    const factor = Math.max(0, Math.min(1, (t - p1.timestamp_seconds) / tSpan))
    const b1 = p1.bounding_box
    const b2 = p2.bounding_box

    return {
      xmin: b1.xmin + (b2.xmin - b1.xmin) * factor,
      ymin: b1.ymin + (b2.ymin - b1.ymin) * factor,
      xmax: b1.xmax + (b2.xmax - b1.xmax) * factor,
      ymax: b1.ymax + (b2.ymax - b1.ymax) * factor,
    }
  }

  // HIGH-FREQUENCY ANIMATION LOOP SYNCED WITH video.currentTime
  useEffect(() => {
    const updateTrackingOverlay = () => {
      if (videoRef.current && containerRef.current) {
        const time = videoRef.current.currentTime
        setCurrentTime(time)

        if (targetTrack && targetTrack.trajectory.length > 0) {
          const traj = targetTrack.trajectory

          if (time < targetTrack.first_seen - 0.5) {
            setTrackStatus('AWAITING')
            setTargetBoxCoords(null)
          } else if (time > targetTrack.last_seen + 0.8) {
            setTrackStatus('ENDED')
            setTargetBoxCoords(null)
          } else {
            // Find nearest trajectory points for current timestamp
            let p1 = traj[0]
            let p2 = traj[traj.length - 1]

            for (let i = 0; i < traj.length - 1; i++) {
              if (time >= traj[i].timestamp_seconds && time <= traj[i + 1].timestamp_seconds) {
                p1 = traj[i]
                p2 = traj[i + 1]
                break
              }
            }

            const currentBBox = interpolateBBox(p1, p2, time)
            const coords = calculateScaledCoords(currentBBox, videoRef.current, containerRef.current)
            setTargetBoxCoords(coords)

            // Check for tracking gaps (> 1.5s)
            const gap = Math.abs(time - p1.timestamp_seconds)
            if (gap > 1.5) {
              setTrackStatus('LOST')
            } else {
              setTrackStatus('TRACKING')
            }
          }
        } else if (activeMatch?.bounding_box) {
          // Fallback static box if no ByteTrack trajectory loaded yet
          const coords = calculateScaledCoords(
            activeMatch.bounding_box,
            videoRef.current,
            containerRef.current
          )
          setTargetBoxCoords(coords)
          setTrackStatus('TRACKING')
        }
      }

      animationFrameRef.current = requestAnimationFrame(updateTrackingOverlay)
    }

    animationFrameRef.current = requestAnimationFrame(updateTrackingOverlay)
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [targetTrack, activeMatch])

  // Keyboard Shortcuts Listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes((e.target as HTMLElement).tagName)) return

      switch (e.code) {
        case 'Space':
          e.preventDefault()
          togglePlay()
          break
        case 'ArrowLeft':
          e.preventDefault()
          if (videoRef.current) videoRef.current.currentTime = Math.max(0, videoRef.current.currentTime - 5)
          break
        case 'ArrowRight':
          e.preventDefault()
          if (videoRef.current) videoRef.current.currentTime = Math.min(maxTimestamp, videoRef.current.currentTime + 5)
          break
        case 'KeyM':
          e.preventDefault()
          toggleMute()
          break
        case 'KeyF':
          e.preventDefault()
          toggleFullscreen()
          break
        default:
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [togglePlay, toggleMute, toggleFullscreen, maxTimestamp])

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
    }
  }

  const jumpToTimestamp = (match: SearchResultItem) => {
    setActiveMatch(match)
    onMatchSelect?.(match)
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

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
      {/* Timeline Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center font-bold">
            <Film className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">{videoTitle} — Dynamic Tracking Workstation</h3>
            <p className="text-xs text-slate-400">
              ByteTrack trajectory multi-object tracking overlay synchronized to video.currentTime
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Show All Tracks Toggle */}
          <label className="flex items-center space-x-2 text-xs font-mono text-slate-300 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={showAllTracks}
              onChange={(e) => setShowAllTracks(e.target.checked)}
              className="rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0"
            />
            <Eye className="w-3.5 h-3.5 text-indigo-400" />
            <span>Show All Tracks</span>
          </label>

          <div className="flex items-center space-x-2 font-mono text-xs text-slate-400 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
            <span>Active Tracks: <strong className="text-emerald-400">{allTracks.length}</strong></span>
          </div>
        </div>
      </div>

      {/* Target Track Summary Banner */}
      {targetTrack && (
        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4 font-mono text-xs shadow-inner">
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-2 text-indigo-400 font-bold bg-indigo-500/10 px-3 py-1 rounded-xl border border-indigo-500/30">
              <Crosshair className="w-4 h-4" />
              <span>TARGET: TRACK-{targetTrack.track_id}</span>
            </span>

            <span className="text-slate-300 capitalize">
              Class: <strong className="text-slate-100">{targetTrack.label}</strong>
            </span>

            <span className="text-slate-400">
              First Seen: <strong className="text-slate-200">{formatDuration(targetTrack.first_seen)}</strong>
            </span>

            <span className="text-slate-400">
              Last Seen: <strong className="text-slate-200">{formatDuration(targetTrack.last_seen)}</strong>
            </span>

            <span className="text-slate-400">
              Frames: <strong className="text-purple-400">{targetTrack.total_frames} keyframes</strong>
            </span>
          </div>

          <div className="flex items-center space-x-2">
            {trackStatus === 'TRACKING' && (
              <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-xl font-bold flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>TRACKING ACTIVE</span>
              </span>
            )}
            {trackStatus === 'LOST' && (
              <span className="bg-amber-500/20 text-amber-400 border border-amber-500/30 px-3 py-1 rounded-xl font-bold flex items-center space-x-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>TRACK TEMPORARILY LOST</span>
              </span>
            )}
            {trackStatus === 'ENDED' && (
              <span className="bg-red-500/20 text-red-400 border border-red-500/30 px-3 py-1 rounded-xl font-bold">
                TRACK ENDED
              </span>
            )}
          </div>
        </div>
      )}

      {/* Video Player Box & Dynamic Tracking Overlay Container */}
      <div ref={containerRef} className="relative aspect-video bg-black rounded-2xl overflow-hidden border border-slate-800 shadow-2xl group">
        <video
          ref={videoRef}
          src={
            videoUrl && videoUrl.endsWith('.mp4')
              ? videoUrl
              : 'http://localhost:8000/data/videos/11111111-1111-1111-1111-111111111111/029841e0-53b6-4748-8114-6c7b74ce5c9e/video_029841e0-53b6-4748-8114-6c7b74ce5c9e.mp4'
          }
          onTimeUpdate={handleTimeUpdate}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          controls
          className="w-full h-full object-contain"
        />

        {/* DYNAMIC TARGET BOUNDING BOX OVERLAY */}
        {targetBoxCoords && (trackStatus === 'TRACKING' || trackStatus === 'LOST') && (
          <div
            className={`absolute border-2 transition-all duration-75 rounded-lg pointer-events-none shadow-2xl ${
              trackStatus === 'LOST'
                ? 'border-amber-400 bg-amber-500/10 shadow-amber-500/30'
                : 'border-emerald-400 bg-emerald-500/15 shadow-[0_0_20px_rgba(52,211,153,0.6)]'
            }`}
            style={{
              left: `${targetBoxCoords.left}px`,
              top: `${targetBoxCoords.top}px`,
              width: `${targetBoxCoords.width}px`,
              height: `${targetBoxCoords.height}px`,
            }}
          >
            <div className="absolute -top-7 left-0 bg-emerald-500 text-black font-extrabold font-mono text-[10px] px-2 py-0.5 rounded shadow-lg uppercase whitespace-nowrap flex items-center space-x-1.5">
              <span>TARGET</span>
              <span>·</span>
              <span>TRACK-{targetTrack?.track_id || activeMatch?.track_id || 1}</span>
              <span>·</span>
              <span>{activeMatch?.label?.toUpperCase() || 'OBJECT'}</span>
              <span>·</span>
              <span>{((activeMatch?.similarity_score || 0.91) * 100).toFixed(1)}%</span>
            </div>
          </div>
        )}

        {/* SECONDARY TRACKS OVERLAY (WHEN "SHOW ALL TRACKS" IS ENABLED) */}
        {showAllTracks &&
          allTracks
            .filter((t) => t.track_id !== targetTrack?.track_id)
            .map((secTrack) => {
              if (currentTime < secTrack.first_seen || currentTime > secTrack.last_seen) return null
              const traj = secTrack.trajectory
              if (traj.length === 0) return null

              let p1 = traj[0]
              let p2 = traj[traj.length - 1]
              for (let i = 0; i < traj.length - 1; i++) {
                if (currentTime >= traj[i].timestamp_seconds && currentTime <= traj[i + 1].timestamp_seconds) {
                  p1 = traj[i]
                  p2 = traj[i + 1]
                  break
                }
              }
              const currentBBox = interpolateBBox(p1, p2, currentTime)
              if (!videoRef.current || !containerRef.current) return null
              const coords = calculateScaledCoords(currentBBox, videoRef.current, containerRef.current)

              return (
                <div
                  key={`sec-track-${secTrack.track_id}`}
                  className="absolute border border-blue-400/80 bg-blue-500/10 rounded-md pointer-events-none shadow-md"
                  style={{
                    left: `${coords.left}px`,
                    top: `${coords.top}px`,
                    width: `${coords.width}px`,
                    height: `${coords.height}px`,
                  }}
                >
                  <span className="absolute -top-5 left-0 bg-slate-900/90 border border-blue-500/40 text-blue-300 font-mono font-bold text-[9px] px-1.5 py-0.5 rounded uppercase">
                    TRACK-{secTrack.track_id} · {secTrack.label}
                  </span>
                </div>
              )
            })}

        {/* Player Controls Bar Overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/95 via-black/70 to-transparent p-4 flex items-center justify-between text-white opacity-95 transition-opacity pointer-events-none z-30">
          <div className="flex items-center space-x-3 pointer-events-auto">
            <button
              onClick={togglePlay}
              className="w-10 h-10 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center transition shadow-lg"
              title="Play/Pause (Space)"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
            </button>

            <button onClick={toggleMute} className="text-slate-300 hover:text-white p-2" title="Mute (M)">
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>

            <span className="font-mono text-xs text-slate-300">
              {formatDuration(currentTime)} / {formatDuration(maxTimestamp)}
            </span>
          </div>

          {/* Speed Selectors & Fullscreen Toggle */}
          <div className="flex items-center space-x-2 pointer-events-auto">
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

            <button
              onClick={toggleFullscreen}
              className="p-2 rounded-xl bg-slate-950/80 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition"
              title="Fullscreen (F)"
            >
              <Maximize className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Interactive Match Timeline Scrubber Bar */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
          <span className="flex items-center space-x-1.5">
            <Zap className="w-4 h-4 text-emerald-400" />
            <span>Interactive Match Timeline Track (Click pin to jump & auto-track)</span>
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
                <div
                  className={`w-3.5 h-6 rounded-md border flex items-center justify-center shadow-lg transition-all ${
                    isSelected
                      ? 'bg-pink-500 border-white shadow-pink-500/50 scale-125 z-30'
                      : match.similarity_score > 0.85
                      ? 'bg-emerald-500 border-emerald-300 shadow-emerald-500/40'
                      : 'bg-indigo-500 border-indigo-300 shadow-indigo-500/30'
                  }`}
                />

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
          <span>Similarity Match Cards — Click 'Follow Track' to auto-track object</span>
          <span className="text-[11px] text-slate-500 font-mono">ByteTrack Target Track Synchronization</span>
        </h4>

        <div className="flex space-x-3 overflow-x-auto pb-3 pt-1 scrollbar-thin scrollbar-thumb-slate-800">
          {results.map((match, idx) => {
            const isSelected = activeMatch?.frame_id === match.frame_id
            return (
              <div
                key={`${match.frame_id}-card-${idx}`}
                onClick={() => jumpToTimestamp(match)}
                className={`w-56 shrink-0 bg-slate-950 border rounded-2xl p-3.5 space-y-3 cursor-pointer transition-all hover:scale-[1.02] ${
                  isSelected ? 'border-pink-500 bg-pink-500/5 ring-1 ring-pink-500' : 'border-slate-800 hover:border-indigo-500/60'
                }`}
              >
                <div className="relative aspect-video rounded-xl bg-black overflow-hidden">
                  <img src={match.crop_url || match.image_url} alt="Match" className="w-full h-full object-cover" />
                  <div className="absolute top-1.5 right-1.5 bg-black/80 backdrop-blur px-2 py-0.5 rounded text-[10px] font-mono font-bold text-emerald-400 border border-slate-700">
                    {(match.similarity_score * 100).toFixed(1)}%
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between items-center text-[11px] font-mono">
                    <span className="text-slate-100 font-bold">{formatDuration(match.timestamp_seconds)}</span>
                    <span className="text-indigo-400 font-bold">TRACK-{match.track_id || 1}</span>
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono truncate">
                    {match.camera_name || 'CAM-01'} · Frame #{match.frame_number}
                  </div>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    jumpToTimestamp(match)
                  }}
                  className={`w-full py-1.5 rounded-xl font-bold text-xs shadow transition flex items-center justify-center space-x-1.5 ${
                    isSelected ? 'bg-pink-600 text-white' : 'bg-indigo-600 hover:bg-indigo-500 text-white'
                  }`}
                >
                  <Crosshair className="w-3.5 h-3.5" />
                  <span>FOLLOW TRACK-{match.track_id || 1}</span>
                </button>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
