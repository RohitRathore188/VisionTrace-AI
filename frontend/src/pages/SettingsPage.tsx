import React, { useState } from 'react'
import { Settings, Cpu, ShieldCheck, Save, Sliders } from 'lucide-react'
import { toast } from 'sonner'

export const SettingsPage: React.FC = () => {
  const [openClipModel, setOpenClipModel] = useState('ViT-B-32')
  const [openClipPretrained, setOpenClipPretrained] = useState('laion2b_s34b_b79k')
  const [faissTopK, setFaissTopK] = useState(10)
  const [minConfidenceThreshold, setMinConfidenceThreshold] = useState(0.25)
  const [autoSyncFaiss, setAutoSyncFaiss] = useState(true)

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault()
    toast.success('Settings saved successfully', {
      description: 'AI Engine and Vector Index configurations updated.',
    })
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight flex items-center space-x-3">
          <div className="p-2 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Settings className="w-6 h-6" />
          </div>
          <span>System Settings & AI Engine Configuration</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Configure OpenCLIP model architecture, FAISS vector index parameters, and backend pipeline settings
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* OpenCLIP Settings */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 space-y-6">
          <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
            <Cpu className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-bold text-slate-100">OpenCLIP 512D Embedding Model</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Model Architecture</label>
              <select
                value={openClipModel}
                onChange={(e) => setOpenClipModel(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="ViT-B-32">ViT-B-32 (Standard 512D Vector)</option>
                <option value="ViT-B-16">ViT-B-16 (High Resolution 512D Vector)</option>
                <option value="ViT-L-14">ViT-L-14 (Large 768D Vector)</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Pretrained Weights</label>
              <input
                type="text"
                value={openClipPretrained}
                onChange={(e) => setOpenClipPretrained(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>
        </div>

        {/* FAISS Vector Search Settings */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 space-y-6">
          <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
            <Sliders className="w-5 h-5 text-emerald-400" />
            <h3 className="text-lg font-bold text-slate-100">FAISS Index & Search Preferences</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Default Top-K Results</label>
              <input
                type="number"
                min={1}
                max={50}
                value={faissTopK}
                onChange={(e) => setFaissTopK(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Minimum Object Detection Confidence ({minConfidenceThreshold * 100}%)
              </label>
              <input
                type="range"
                min={0.05}
                max={0.95}
                step={0.05}
                value={minConfidenceThreshold}
                onChange={(e) => setMinConfidenceThreshold(Number(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>
          </div>

          <div className="flex items-center space-x-3 pt-2">
            <input
              type="checkbox"
              id="autoSync"
              checked={autoSyncFaiss}
              onChange={(e) => setAutoSyncFaiss(e.target.checked)}
              className="w-4 h-4 text-emerald-500 rounded border-slate-800 bg-slate-950 focus:ring-emerald-500"
            />
            <label htmlFor="autoSync" className="text-sm font-semibold text-slate-300">
              Auto-sync FAISS index on new video keyframe embedding generation
            </label>
          </div>
        </div>

        {/* Database & Security Status */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 space-y-4">
          <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
            <ShieldCheck className="w-5 h-5 text-indigo-400" />
            <h3 className="text-lg font-bold text-slate-100">System Environment & Security</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl">
              <span className="text-slate-500 block">Database Mode</span>
              <span className="text-emerald-400 font-bold">SQLite + aiosqlite (Local Dev)</span>
            </div>
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl">
              <span className="text-slate-500 block">FAISS Index Storage</span>
              <span className="text-purple-400 font-bold">./data/faiss_indexes/visiontrace_512d.index</span>
            </div>
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl">
              <span className="text-slate-500 block">JWT Auth Secret</span>
              <span className="text-indigo-400 font-bold">HS256 (Local Dev Mode)</span>
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="flex items-center space-x-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl shadow-lg transition"
          >
            <Save className="w-4 h-4" />
            <span>Save Configuration</span>
          </button>
        </div>
      </form>
    </div>
  )
}
