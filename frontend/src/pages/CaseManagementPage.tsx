import React, { useState, useEffect } from 'react'
import { SecurityService, CaseItem } from '@/services/securityService'
import {
  Briefcase,
  Plus,
  Shield,
  MessageSquare,
} from 'lucide-react'

export const CaseManagementPage: React.FC = () => {
  const [cases, setCases] = useState<CaseItem[]>([])
  const [selectedCase, setSelectedCase] = useState<CaseItem | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [newNote, setNewNote] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newDesc, setNewDesc] = useState('')
  const [newPriority, setNewPriority] = useState('medium')

  const fetchCases = async () => {
    try {
      const data = await SecurityService.getCases()
      setCases(data)
      if (data.length > 0 && !selectedCase) {
        setSelectedCase(data[0])
      }
    } catch (err) {
      console.error('Failed to load cases:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCases()
  }, [])

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim()) return
    try {
      const created = await SecurityService.createCase(newTitle, newDesc, newPriority)
      setCases([created, ...cases])
      setSelectedCase(created)
      setShowCreateModal(false)
      setNewTitle('')
      setNewDesc('')
    } catch (err) {
      console.error('Failed to create case:', err)
    }
  }

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedCase || !newNote.trim()) return
    try {
      const updated = await SecurityService.addCaseNote(selectedCase.id, newNote)
      setCases(cases.map((c) => (c.id === updated.id ? updated : c)))
      setSelectedCase(updated)
      setNewNote('')
    } catch (err) {
      console.error('Failed to add note:', err)
    }
  }

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'critical':
        return <span className="bg-red-500/20 text-red-400 border border-red-500/30 text-[10px] font-mono font-bold px-2 py-0.5 rounded-md uppercase">Critical</span>
      case 'high':
        return <span className="bg-amber-500/20 text-amber-400 border border-amber-500/30 text-[10px] font-mono font-bold px-2 py-0.5 rounded-md uppercase">High</span>
      case 'medium':
        return <span className="bg-blue-500/20 text-blue-400 border border-blue-500/30 text-[10px] font-mono font-bold px-2 py-0.5 rounded-md uppercase">Medium</span>
      default:
        return <span className="bg-slate-800 text-slate-400 text-[10px] font-mono font-bold px-2 py-0.5 rounded-md uppercase">Low</span>
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <Briefcase className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-100 uppercase tracking-tight flex items-center space-x-2">
              <span>Incident Case Management Locker</span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Official security investigations, chain of custody tracking, and evidence file notes
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2.5 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/25 flex items-center space-x-2 transition"
        >
          <Plus className="w-4 h-4" />
          <span>New Incident Case File</span>
        </button>
      </div>

      {/* Main Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Case List */}
        <div className="lg:col-span-5 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 px-1 flex items-center space-x-1.5">
            <Shield className="w-3.5 h-3.5 text-indigo-400" />
            <span>Active Incident Files ({cases.length})</span>
          </h3>

          {isLoading ? (
            <div className="py-12 text-center text-xs text-slate-400">Loading incident cases...</div>
          ) : cases.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 border border-dashed border-slate-800 rounded-2xl">
              No incident cases found
            </div>
          ) : (
            cases.map((c) => (
              <div
                key={c.id}
                onClick={() => setSelectedCase(c)}
                className={`p-4 rounded-2xl border cursor-pointer transition-all duration-200 space-y-2 ${
                  selectedCase?.id === c.id
                    ? 'bg-indigo-600/15 border-indigo-500/60 shadow-lg shadow-indigo-600/10'
                    : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-indigo-400">{c.case_number}</span>
                  {getPriorityBadge(c.priority)}
                </div>

                <h4 className="text-sm font-bold text-slate-100 truncate">{c.title}</h4>

                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1">
                  <span className="capitalize text-slate-300">Status: {c.status}</span>
                  <span>{new Date(c.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Right Column: Case Details & Timeline Notes */}
        <div className="lg:col-span-7">
          {selectedCase ? (
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
              <div className="border-b border-slate-800 pb-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-lg border border-indigo-500/20">
                    {selectedCase.case_number}
                  </span>
                  {getPriorityBadge(selectedCase.priority)}
                </div>

                <h2 className="text-lg font-extrabold text-slate-100">{selectedCase.title}</h2>
                <p className="text-xs text-slate-300 bg-slate-950 p-3 rounded-xl border border-slate-800">
                  {selectedCase.description || 'No detailed description recorded.'}
                </p>
              </div>

              {/* Investigator Timeline Notes */}
              <div className="space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Investigator Chain-of-Custody Log ({selectedCase.notes_json?.length || 0})</span>
                </h4>

                <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
                  {(selectedCase.notes_json || []).map((note, nIdx) => (
                    <div key={nIdx} className="bg-slate-950 border border-slate-800/80 p-3.5 rounded-2xl space-y-1">
                      <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                        <span className="text-indigo-400 font-bold">{note.author}</span>
                        <span>{new Date(note.timestamp).toLocaleString()}</span>
                      </div>
                      <p className="text-xs text-slate-200">{note.text}</p>
                    </div>
                  ))}
                </div>

                {/* Add Note Form */}
                <form onSubmit={handleAddNote} className="flex items-center space-x-2 pt-2">
                  <input
                    type="text"
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    placeholder="Append investigator log entry or findings..."
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shrink-0"
                  >
                    Append Log
                  </button>
                </form>
              </div>
            </div>
          ) : (
            <div className="py-20 border border-dashed border-slate-800 rounded-3xl text-center text-slate-500 text-xs">
              Select an incident case to view investigation details
            </div>
          )}
        </div>
      </div>

      {/* Create Case Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
              <Briefcase className="w-5 h-5 text-indigo-400" />
              <span>Create New Incident Case File</span>
            </h3>

            <form onSubmit={handleCreateCase} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Case Title</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Unauthorized Entrance Access"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Description / Report</label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Incident details..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 h-20"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Priority</label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div className="flex items-center justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold"
                >
                  Save Case
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
