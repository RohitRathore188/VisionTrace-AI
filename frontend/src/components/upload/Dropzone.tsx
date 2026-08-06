import React, { useState, useRef, DragEvent, ChangeEvent } from 'react'
import { UploadCloud, Film, AlertCircle, FileCheck } from 'lucide-react'
import { ALLOWED_VIDEO_EXTENSIONS, MAX_VIDEO_SIZE_MB, formatBytes } from '@/lib/videoValidation'

interface DropzoneProps {
  onFileSelect: (file: File) => void
  disabled?: boolean
  isValidating?: boolean
  error?: string | null
}

export const Dropzone: React.FC<DropzoneProps> = ({
  onFileSelect,
  disabled = false,
  isValidating = false,
  error,
}) => {
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    if (!disabled) {
      setIsDragOver(true)
    }
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)

    if (disabled) return

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      onFileSelect(files[0])
    }
  }

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0])
    }
  }

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  return (
    <div
      onClick={handleClick}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300
        flex flex-col items-center justify-center min-h-[260px] group overflow-hidden
        ${
          isDragOver
            ? 'border-indigo-500 bg-indigo-500/10 scale-[1.01] shadow-lg shadow-indigo-500/20'
            : error
            ? 'border-red-500/60 bg-red-500/5 hover:border-red-500'
            : 'border-slate-700 bg-slate-900/60 hover:border-indigo-500/80 hover:bg-slate-900/90'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''}
      `}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept={ALLOWED_VIDEO_EXTENSIONS.join(',')}
        onChange={handleFileChange}
        className="hidden"
        disabled={disabled}
      />

      {/* Decorative gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-tr from-indigo-500/5 via-transparent to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

      {isValidating ? (
        <div className="flex flex-col items-center space-y-4">
          <div className="w-12 h-12 rounded-full border-4 border-indigo-500/30 border-t-indigo-500 animate-spin" />
          <p className="text-sm font-medium text-slate-300">Validating video file format and extracting metadata...</p>
        </div>
      ) : (
        <>
          <div className="relative mb-4">
            <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-110 group-hover:bg-indigo-500/20 transition-all duration-300">
              {isDragOver ? <FileCheck className="w-8 h-8 animate-bounce" /> : <UploadCloud className="w-8 h-8" />}
            </div>
            <div className="absolute -bottom-1 -right-1 w-7 h-7 rounded-lg bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-300">
              <Film className="w-4 h-4" />
            </div>
          </div>

          <h3 className="text-lg font-semibold text-slate-100 mb-1">
            {isDragOver ? 'Drop video here to upload' : 'Drag & drop surveillance video'}
          </h3>
          <p className="text-sm text-slate-400 mb-4 max-w-sm">
            or <span className="text-indigo-400 font-medium underline underline-offset-4">browse files</span> on your device
          </p>

          {/* Extension Pills */}
          <div className="flex flex-wrap items-center justify-center gap-2 mb-4">
            {ALLOWED_VIDEO_EXTENSIONS.map((ext) => (
              <span
                key={ext}
                className="px-2.5 py-1 text-xs font-semibold rounded-md bg-slate-800/80 text-slate-300 border border-slate-700/60 uppercase"
              >
                {ext.replace('.', '')}
              </span>
            ))}
            <span className="text-xs text-slate-500">Up to {formatBytes(MAX_VIDEO_SIZE_MB * 1024 * 1024)}</span>
          </div>

          {error && (
            <div className="flex items-center space-x-2 text-xs text-red-400 bg-red-500/10 border border-red-500/20 px-3 py-1.5 rounded-lg">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </>
      )}
    </div>
  )
}
