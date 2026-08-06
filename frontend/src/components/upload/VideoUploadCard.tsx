import React from 'react'
import { Upload, Film, Tag, FileText, CheckCircle2 } from 'lucide-react'
import { useVideoUpload } from '@/hooks/useVideoUpload'
import { Dropzone } from './Dropzone'
import { VideoPreview } from './VideoPreview'
import { UploadProgressBar } from './UploadProgressBar'

interface VideoUploadCardProps {
  onUploadSuccess?: () => void
}

export const VideoUploadCard: React.FC<VideoUploadCardProps> = ({ onUploadSuccess }) => {
  const {
    file,
    previewUrl,
    metadata,
    validationError,
    isValidating,
    title,
    setTitle,
    description,
    setDescription,
    progress,
    uploadedVideo,
    handleSelectFile,
    resetUpload,
    startUpload,
    pauseUpload,
    resumeUpload,
    cancelUpload,
  } = useVideoUpload()

  const isUploading = progress.isUploading
  const isCompleted = progress.isCompleted

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    await startUpload()
    if (onUploadSuccess) {
      onUploadSuccess()
    }
  }

  return (
    <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-2xl backdrop-blur-xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
            <Film className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100">Upload Video Asset</h2>
            <p className="text-xs text-slate-400">Ingest surveillance footage into VisionTrace AI pipeline</p>
          </div>
        </div>

        {file && !isUploading && !isCompleted && (
          <button
            type="button"
            onClick={resetUpload}
            className="text-xs font-semibold text-slate-400 hover:text-slate-200 transition"
          >
            Clear Selection
          </button>
        )}
      </div>

      {!file ? (
        <Dropzone
          onFileSelect={handleSelectFile}
          isValidating={isValidating}
          error={validationError}
        />
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Preview Player */}
          {previewUrl && (
            <VideoPreview
              src={previewUrl}
              file={file}
              metadata={metadata}
              onReset={resetUpload}
              disabled={isUploading || isCompleted}
            />
          )}

          {/* Video Metadata Form Fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                <Tag className="w-3.5 h-3.5 text-indigo-400" />
                <span>Video Title / Camera ID</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Parking Lot Entrance North - Cam 04"
                disabled={isUploading || isCompleted}
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 transition"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                <FileText className="w-3.5 h-3.5 text-purple-400" />
                <span>Description / Investigation Notes</span>
              </label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g. Night vision recording from 2026-08-05 shift"
                disabled={isUploading || isCompleted}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 transition"
              />
            </div>
          </div>

          {/* Upload Progress Bar */}
          {(isUploading || isCompleted || progress.error) && (
            <UploadProgressBar
              progress={progress}
              onPause={pauseUpload}
              onResume={resumeUpload}
              onCancel={cancelUpload}
            />
          )}

          {/* Success Banner */}
          {isCompleted && uploadedVideo && (
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-4 flex items-center justify-between text-emerald-300">
              <div className="flex items-center space-x-3">
                <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
                <div>
                  <h4 className="text-sm font-bold">Video Successfully Uploaded</h4>
                  <p className="text-xs text-emerald-400/80">
                    Video ID: <code className="bg-black/30 px-1.5 py-0.5 rounded text-[11px] font-mono">{uploadedVideo.id}</code> (Status: Ready for search)
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={resetUpload}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition shadow-md"
              >
                Upload Another Video
              </button>
            </div>
          )}

          {/* Submit Action Button */}
          {!isUploading && !isCompleted && (
            <button
              type="submit"
              className="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-500 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm shadow-xl shadow-indigo-600/25 flex items-center justify-center space-x-2 transition hover:scale-[1.005]"
            >
              <Upload className="w-4 h-4" />
              <span>Start Upload to Supabase Storage</span>
            </button>
          )}
        </form>
      )}
    </div>
  )
}
